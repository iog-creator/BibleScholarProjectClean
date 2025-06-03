#!/usr/bin/env python3
"""
MCP Server for BibleScholarProjectv2
Provides tool-based rule enforcement for Cursor and automation scripts.
MCP only runs on Port 8000 and will not start if another instance is running. It will give errors. 

"""
import sys
import os
import socket
import time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Add project root to sys.path for 'src' imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rules_loader import load_rules
import json
import psycopg2
from psycopg2.extras import DictCursor
import subprocess
import datetime
import logging
import pandas as pd
import jsonschema
import requests
import asyncio
from fastapi import FastAPI, Request, Response, APIRouter, status, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from jsonrpcserver import method, Result, Success, dispatch
from sse_starlette.sse import EventSourceResponse
import importlib.util
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/utils')))
from vector_search import search_verses_by_semantic_similarity
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from logging.handlers import RotatingFileHandler
import tempfile
import scripts.progress_tracker as progress_tracker
from dotenv import load_dotenv

print('MCP SERVER: scripts/mcp_server.py is executing (top of file)')

# --- LOGGING CONFIGURATION ---
# Always show INFO and above in the terminal for AI and human debugging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Changed from WARNING to INFO for full debug output

# File handler remains at INFO (or DEBUG if needed)
def get_log_file_handler(log_file_path):
    try:
        return RotatingFileHandler(log_file_path, maxBytes=102400, backupCount=1, encoding='utf-8')
    except PermissionError:
        temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        print(f"[WARNING] Log file {log_file_path} is locked. Using temporary log file: {temp_log.name}")
        return RotatingFileHandler(temp_log.name, maxBytes=102400, backupCount=1, encoding='utf-8')

log_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs/mcp_server.log'))
file_handler = get_log_file_handler(log_file_path)
file_handler.setLevel(logging.INFO)  # Keep at INFO, or set to DEBUG if you want even more detail

# Custom filter to suppress file watcher/file change noise
class SuppressNoiseFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # Suppress 'change detected' and similar file watcher noise
        if 'change detected' in msg or 'watchfiles' in record.name:
            return False
        return True

file_handler.addFilter(SuppressNoiseFilter())
console_handler.addFilter(SuppressNoiseFilter())

# Prevent duplicate handlers
root_logger = logging.getLogger()
for h in list(root_logger.handlers):
    root_logger.removeHandler(h)

logging.basicConfig(
    level=logging.INFO,  # Always enable INFO and DEBUG logs
    handlers=[file_handler, console_handler],
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info('MCP SERVER DEBUG MARKER: scripts/mcp_server.py loaded')

logging.getLogger("watchfiles").setLevel(logging.WARNING)
logging.getLogger("watchdog").setLevel(logging.WARNING)
logging.getLogger("watchfiles").addFilter(SuppressNoiseFilter())
logging.getLogger("watchdog").addFilter(SuppressNoiseFilter())

app = FastAPI()

# Database connection
try:
    load_dotenv()
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor(cursor_factory=DictCursor)
except Exception as e:
    logger.error(f"Database connection failed: {str(e)}")
    cursor = None

# Available tools
AVAILABLE_TOOLS = [
    "check_ports",
    "verify_data",
    "run_query",
    "enforce_etl_guidelines",
    "semantic_search",
    "list_lmstudio_models",
    "log_action"
]
logger.info(f"AVAILABLE_TOOLS limited to: {AVAILABLE_TOOLS}")
# Commented out unused tools for reliability
# "terminate_processes",
# "suggest_incremental_change",
# "run_test",
# "get_file_context",
# "update_docs",
# "normalize_reference",
# "check_pandas_nulls",
# "enforce_pandas_types",
# "validate_tvtms_counts",
# "check_tvtms_format",
# "validate_json_schema",

# Dynamic rule loading
DYNAMIC_RULES = load_rules()
logger.info(f"Loaded {len(DYNAMIC_RULES)} rules at startup: {[r['name'] for r in DYNAMIC_RULES]}")
DYNAMIC_TOOLS = {}

PORT = 8000
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs/mcp_server.log'))

RULES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.cursor/rules'))

# --- Teaching Mode (Beginner explanations) ---
teaching_mode = True  # Always on for now

def explain(term, meaning):
    """Return a subtle explanation if teaching_mode is on."""
    if teaching_mode:
        return f" ({meaning})"
    return ""

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Kill any process using the specified port, with retries and detailed logging."""
    for attempt in range(3):
        try:
            # Check if port is in use
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
            lines = [l for l in result.stdout.splitlines() if f":{port} " in l]
            if not lines:
                logger.info(f"Port {port} is free (attempt {attempt+1})")
                return True
            pids = set()
            for l in lines:
                parts = l.split()
                if len(parts) >= 5:
                    pids.add(parts[-1])
            for pid in pids:
                try:
                    subprocess.run(["taskkill", "/F", "/PID", pid], check=True)
                    logger.info(f"Killed process {pid} on port {port} (attempt {attempt+1})")
                except Exception as e:
                    logger.error(f"Failed to kill process {pid} on port {port}: {e}")
            time.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"Error checking/killing port {port} (attempt {attempt+1}): {e}")
            time.sleep(2 ** attempt)
    logger.error(f"Failed to free port {port} after 3 attempts")
    return False

if is_port_in_use(PORT):
    killed = kill_process_on_port(PORT)
    time.sleep(2)
    if is_port_in_use(PORT):
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{time.ctime()}] ERROR: Port {PORT} is still in use. Exiting.\n")
        print(f"ERROR: Port {PORT} is still in use. Exiting.")
        sys.exit(1)
    else:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{time.ctime()}] Port {PORT} was in use but is now free.\n")

def register_dynamic_tools():
    """Register dynamic tools for each loaded rule. Log actions."""
    global DYNAMIC_TOOLS, AVAILABLE_TOOLS
    DYNAMIC_TOOLS = {}
    logger.info(f"Registering dynamic tools for {len(DYNAMIC_RULES)} rules: {[r['name'] for r in DYNAMIC_RULES]}")
    for rule in DYNAMIC_RULES:
        # Log the code_snippet for debugging
        logger.info(f"Rule {rule['name']} code_snippet: {repr(rule.get('code_snippet', 'None'))}")
        tool_name = f"enforce_rule_{rule['name']}"
        def make_tool(rule):
            def tool_func(params=None):
                logger.info(f"Enforcing rule: {rule['name']}, code_snippet: {repr(rule.get('code_snippet', 'None'))}")
                # If the rule has a code_snippet, execute it in a restricted namespace
                if rule.get('code_snippet'):
                    namespace = {'params': params or {}, 'pd': pd, 'result': None}
                    try:
                        exec(rule['code_snippet'], namespace)
                        result = namespace.get('result')
                        return {
                            "status": "success",
                            "rule_name": rule['name'],
                            "description": rule['description'],
                            "alwaysApply": rule['alwaysApply'],
                            "type": rule['type'],
                            "globs": rule['globs'],
                            "raw": rule['raw'],
                            "code_snippet": rule['code_snippet'],
                            "enforcement_result": result
                        }
                    except Exception as e:
                        return {
                            "status": "error",
                            "rule_name": rule['name'],
                            "description": rule['description'],
                            "alwaysApply": rule['alwaysApply'],
                            "type": rule['type'],
                            "globs": rule['globs'],
                            "raw": rule['raw'],
                            "code_snippet": rule['code_snippet'],
                            "error": str(e)
                        }
                # No code_snippet: return metadata only
                return {
                    "status": "success",
                    "rule_name": rule['name'],
                    "description": rule['description'],
                    "alwaysApply": rule['alwaysApply'],
                    "type": rule['type'],
                    "globs": rule['globs'],
                    "raw": rule['raw']
                }
            return tool_func
        DYNAMIC_TOOLS[tool_name] = make_tool(rule)
    # Update AVAILABLE_TOOLS
    dynamic_tool_names = list(DYNAMIC_TOOLS.keys())
    for t in dynamic_tool_names:
        if t not in AVAILABLE_TOOLS:
            AVAILABLE_TOOLS.append(t)
    logger.info(f"Registered {len(DYNAMIC_TOOLS)} dynamic rule tools: {dynamic_tool_names}")

register_dynamic_tools()

@app.get("/sse-cursor")
async def sse_cursor():
    async def event_generator():
        # Initial server_info event
        yield {
            "event": "server_info",
            "data": json.dumps({
                "version": "0.2.0",
                "offerings": AVAILABLE_TOOLS,
                "server_name": "general-project-mcp"
            })
        }
        # Session created event
        yield {
            "event": "session_created",
            "data": json.dumps({"session_id": "session_123"})
        }
        # Heartbeat events
        while True:
            yield {
                "event": "heartbeat",
                "data": json.dumps({"timestamp": int(datetime.datetime.now().timestamp() * 1000)})
            }
            await asyncio.sleep(30)  # Heartbeat every 30 seconds

    return EventSourceResponse(event_generator())

@app.post("/sse-cursor")
async def sse_cursor_post(request: Request):
    # Forward POSTs to the JSON-RPC handler for MCP compatibility
    return await jsonrpc(request)

@app.get("/ping")
async def ping():
    print("/ping called")
    logger.info("/ping called" + explain("ping", "a quick check to see if the server is running"))
    return {"status": "ok", "explanation": "pong = server is alive" if teaching_mode else "pong"}

@app.post("/jsonrpc")
async def jsonrpc(request: Request):
    logger.info("Received JSON-RPC request")
    try:
        body = await request.body()
        if not body:
            logger.error("Empty request body")
            return JSONResponse(
                content={"jsonrpc": "2.0", "error": {"code": -32600, "message": "Empty request body"}, "id": None},
                status_code=400
            )
        body_str = body.decode("utf-8")
        logger.info(f"Raw request: {body_str}")
        try:
            json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            return JSONResponse(
                content={"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Invalid JSON: {str(e)}"}, "id": None},
                status_code=400
            )
        response = dispatch(body_str)
        logger.info(f"Dispatch response: {response}")
        if hasattr(response, "content"):
            resp_content = json.loads(response.content)
        else:
            resp_content = response
        return JSONResponse(content=resp_content, status_code=200)
    except Exception as e:
        logger.error(f"JSON-RPC error: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": None},
            status_code=500
        )

@app.post("/rpc")
async def rpc_alias(request: Request):
    """Alias for /rpc endpoint to support JSON-RPC calls."""
    return await jsonrpc(request)

@method
def listOfferings() -> Result:
    offerings = list(AVAILABLE_TOOLS)
    # Add dynamic tools if not already present
    for t in DYNAMIC_TOOLS.keys():
        if t not in offerings:
            offerings.append(t)
    return Success({"offerings": offerings})

def log_interaction(tool_name: str, params: dict, result):
    try:
        print(f"log_interaction called for {tool_name}")
        logger.info(f"log_interaction called for {tool_name}")
        import json
        def is_json_serializable_type(obj):
            return isinstance(obj, (dict, list, str, int, float, bool, type(None)))
        def unwrap(obj):
            seen = set()
            while not is_json_serializable_type(obj):
                if id(obj) in seen:
                    break  # Prevent infinite loops
                seen.add(id(obj))
                if hasattr(obj, "_value"):
                    obj = obj._value
                    continue
                if hasattr(obj, "result"):
                    obj = obj.result
                    continue
                break
            return obj
        actual_result = unwrap(result)
        print(f"[DEBUG] Final unwrapped result type: {type(actual_result)}; repr: {repr(actual_result)}")
        logger.info(f"[DEBUG] Final unwrapped result type: {type(actual_result)}; repr: {repr(actual_result)}")
        # Fallback: if not serializable, use str and log a warning
        try:
            json.dumps(actual_result)
        except Exception as e:
            print(f"[WARN] Result not serializable, using str: {e}")
            logger.warning(f"[WARN] Result not serializable, using str: {e}")
            actual_result = str(actual_result)
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "tool_name": tool_name,
            "params": params,
            "result": actual_result
        }
        with open("logs/interaction.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, default=str) + "\n")
        logger.info(f"Logged interaction for {tool_name}")
        generate_rule_from_interaction(tool_name, params, actual_result)
    except Exception as e:
        print(f"log_interaction error: {e}")
        logger.error(f"log_interaction error: {e}")

def generate_rule_from_interaction(tool_name: str, params: dict, result: dict):
    try:
        print(f"generate_rule_from_interaction called for {tool_name}")
        logger.info(f"generate_rule_from_interaction called for {tool_name}")
        if result.get("status") != "success":
            print(f"generate_rule_from_interaction: result not success: {result}")
            return
        rule_name = f"auto_{tool_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        rule_content = f"""
---
name: {rule_name}
description: Auto-generated from {tool_name} interaction
alwaysApply: false
type: automation
globs: ["*.py", "*.sql"]
---
Tool: {tool_name}
Params: {json.dumps(params, indent=2)}
Result: {json.dumps(result, indent=2)}
```python
params = {json.dumps(params)}
result = {json.dumps(result)}
```
"""
        rule_path = f".cursor/rules/automation/{rule_name}.mdc"
        os.makedirs(".cursor/rules/automation", exist_ok=True)
        with open(rule_path, "w", encoding="utf-8") as f:
            f.write(rule_content)
        logger.info(f"Generated rule: {rule_name}")
    except Exception as e:
        print(f"generate_rule_from_interaction error: {e}")
        logger.error(f"generate_rule_from_interaction error: {e}")

def prune_rules():
    """Prune outdated automation rules, keeping backups"""
    import glob, re
    rule_files = glob.glob(".cursor/rules/automation/auto_*.mdc")
    for rule_file in rule_files:
        rule_name = os.path.basename(rule_file).replace(".mdc", "")
        with open(rule_file, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"(\d{8}_\d{6})", rule_name)
        if match:
            rule_date = datetime.datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
            if (datetime.datetime.now() - rule_date).days > 30:
                backup_content = f"\n\n# Backup (ignore unless restore needed)\n{content}"
                with open(rule_file, "a", encoding="utf-8") as f:
                    f.write(backup_content)
                with open(rule_file, "w", encoding="utf-8") as f:
                    f.write("# Pruned rule - ready for new content\n")
                logger.info(f"Pruned rule: {rule_name}, backup appended")

@method
def executeTool(tool_name: str, params: dict) -> Result:
    logger.info(f"Executing tool: {tool_name} with params: {params}")
    # Dynamic tools
    if tool_name in DYNAMIC_TOOLS:
        try:
            result = Success(DYNAMIC_TOOLS[tool_name](params))
            log_interaction(tool_name, params, result)
            return result
        except Exception as e:
            result = Success({"status": "error", "message": str(e)})
            log_interaction(tool_name, params, result)
            return result
    if tool_name not in AVAILABLE_TOOLS:
        result = Success({"status": "error", "message": f"Tool {tool_name} not found"})
        log_interaction(tool_name, params, result)
        return result
    try:
        if tool_name == "check_ports":
            result = Success(check_ports(params.get("ports", [])))
        elif tool_name == "verify_data":
            query = params.get("query")
            params_list = params.get("params", [])
            result = Success(verify_data(query, params_list))
        elif tool_name == "run_query":
            query = params.get("query")
            params_list = params.get("params", [])
            result = Success(run_query(query, params_list))
        elif tool_name == "enforce_etl_guidelines":
            data_json = params.get("data_json")
            result = Success(enforce_etl_guidelines(data_json))
        elif tool_name == "semantic_search":
            query = params.get("query")
            translation = params.get("translation", "KJV")
            limit = params.get("limit", 10)
            result = Success(semantic_search(query, translation, limit))
        elif tool_name == "list_lmstudio_models":
            result = Success(list_lmstudio_models())
        elif tool_name == "log_action":
            log_file = params.get("log_file")
            action_message = params.get("action_message")
            result = Success(log_action(log_file, action_message))
        else:
            result = Success({"status": "error", "message": f"Tool {tool_name} not implemented"})
        log_interaction(tool_name, params, result)
        return result
    except Exception as e:
        result = Success({"status": "error", "message": str(e)})
        log_interaction(tool_name, params, result)
        return result

@method
def reload_rules() -> Result:
    """Reload rules from disk and re-register dynamic tools. Log reload."""
    global DYNAMIC_RULES
    DYNAMIC_RULES = load_rules()
    logger.info(f"Reloaded {len(DYNAMIC_RULES)} rules at startup: {[r['name'] for r in DYNAMIC_RULES]}")
    register_dynamic_tools()
    logger.info(f"Reloaded {len(DYNAMIC_RULES)} rules and re-registered dynamic tools.")
    return Success({"status": "success", "message": f"Reloaded {len(DYNAMIC_RULES)} rules."})

def check_ports(ports):
    try:
        for port in ports:
            result = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True)
            if result.stdout:
                return {"status": "error", "message": f"Port {port} is in use!"}
        return {"status": "success", "message": "All ports are free."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def verify_data(query, params):
    if not cursor:
        return {"status": "error", "message": "Database connection not available."}
    try:
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        if results:
            return {"status": "success", "data_present": True, "results": results}
        return {"status": "success", "data_present": False}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_query(query, params):
    if not cursor:
        return {"status": "error", "message": "Database connection not available."}
    try:
        cursor.execute(query, params)
        return {"status": "success", "results": [dict(row) for row in cursor.fetchall()]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def enforce_etl_guidelines(data_json):
    try:
        data = pd.DataFrame(json.loads(data_json))
        required_columns = ["id", "value"]  # Example; adjust per project
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            return {"status": "error", "message": f"Missing required columns: {missing_columns}"}
        if data.duplicated().any():
            return {"status": "error", "message": "Data contains duplicates"}
        return {"status": "success", "message": "Data validated for ETL processing"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def semantic_search(query, translation="KJV", limit=10):
    try:
        results = search_verses_by_semantic_similarity(query, translation, limit)
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_lmstudio_models():
    """List currently loaded models from LM Studio via /v1/models endpoint."""
    lmstudio_url = os.getenv("LM_STUDIO_API_URL", "http://localhost:1234/v1/models")
    try:
        resp = requests.get(lmstudio_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {"status": "success", "models": data.get("data", data)}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def log_action(log_file, action_message):
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {action_message}\n")
        return {"status": "success", "message": f"Logged to {log_file}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/rules")
async def list_rules():
    # Return all loaded rules with their metadata
    return {"status": "success", "rules": DYNAMIC_RULES}

@app.get("/rules/enforce/{rule_name}")
async def enforce_rule(rule_name: str):
    tool_name = f"enforce_rule_{rule_name}"
    if tool_name not in DYNAMIC_TOOLS:
        return {"status": "error", "message": f"Tool {tool_name} not found"}
    try:
        result = DYNAMIC_TOOLS[tool_name]({})
        return {"status": "success", "rule": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/rules/enforce/{rule_name}")
async def enforce_rule_post(rule_name: str, request: Request):
    tool_name = f"enforce_rule_{rule_name}"
    if tool_name not in DYNAMIC_TOOLS:
        return JSONResponse(content={"status": "error", "message": f"Tool {tool_name} not found"}, status_code=status.HTTP_404_NOT_FOUND)
    try:
        params = await request.json()
    except Exception:
        params = {}
    try:
        result = DYNAMIC_TOOLS[tool_name](params)
        return JSONResponse(content={"status": "success", "rule": result}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/progress/award")
async def award_points_endpoint(request: Request):
    data = await request.json()
    user = data.get("user")
    skill = data.get("skill")
    points = data.get("points")
    if not user or not skill or not isinstance(points, int):
        raise HTTPException(status_code=400, detail="Invalid payload: requires 'user' (str), 'skill' (str), 'points' (int)")
    try:
        progress_tracker.award_points(user, skill, points)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/progress")
async def get_progress(user: str):
    try:
        totals = progress_tracker.get_current_points(user)
        return {"status": "success", "user": user, "points": totals}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/progress/report")
async def progress_report(user: str, period: str):
    try:
        report = progress_tracker.get_report(user, period)
        return {"status": "success", "user": user, "report": report}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/progress/snapshot")
async def take_snapshot_endpoint(request: Request):
    data = await request.json()
    user = data.get("user")
    period = data.get("period")
    if not user or not period:
        raise HTTPException(status_code=400, detail="Invalid payload: requires 'user' and 'period'")
    try:
        progress_tracker.take_snapshot(user, period)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/progress/snapshot")
async def get_snapshot_endpoint(user: str = Query(...), period: str = Query(...)):
    try:
        snap = progress_tracker.get_snapshot(user, period)
        return {"status": "success", "user": user, "period": period, "snapshot": snap}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/{full_path:path}")
async def catch_all_post(full_path: str, request: Request):
    body = await request.body()
    print(f"[CATCH-ALL] POST to /{full_path} with body: {body}")
    logger.info(f"[CATCH-ALL] POST to /{full_path} with body: {body}")
    return JSONResponse(content={"status": "caught", "path": full_path}, status_code=404)

class RuleChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and (event.src_path.endswith(".mdc") or event.src_path.endswith(".md")):
            logger.info(f"Rule modified: {event.src_path}, reloading rules...")
            ws_log = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs/workspace_setup.log'))
            with open(ws_log, 'a', encoding='utf-8') as wsp:
                wsp.write(f"[{time.ctime()}] Rule modified: {event.src_path}, rules reloaded\n")
            reload_rules()

    def on_created(self, event):
        if not event.is_directory and (event.src_path.endswith(".mdc") or event.src_path.endswith(".md")):
            logger.info(f"Rule created: {event.src_path}, reloading rules...")
            ws_log = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs/workspace_setup.log'))
            with open(ws_log, 'a', encoding='utf-8') as wsp:
                wsp.write(f"[{time.ctime()}] Rule created: {event.src_path}, rules reloaded\n")
            reload_rules()

    def on_deleted(self, event):
        if not event.is_directory and (event.src_path.endswith(".mdc") or event.src_path.endswith(".md")):
            logger.info(f"Rule deleted: {event.src_path}, checking cleanup and reloading rules...")
            ws_log = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs/workspace_setup.log'))
            with open(ws_log, 'a', encoding='utf-8') as wsp:
                wsp.write(f"[{time.ctime()}] Rule deleted: {event.src_path}, cleanup triggered\n")
            cleanup_auto_rules()
            reload_rules()

    def on_any_event(self, event):
        # Retain for compatibility, but prefer explicit methods above
        pass

def start_rule_watcher():
    observer = Observer()
    observer.schedule(RuleChangeHandler(), path=RULES_DIR, recursive=False)
    observer.start()
    logger.info(f"Started rule change watcher on {RULES_DIR}")

# Start rule watcher in a background thread at server startup
threading.Thread(target=start_rule_watcher, daemon=True).start()

# --- 2. Add rule file cleanup logic (limit to 100 auto-generated rules) ---
def cleanup_auto_rules():
    rule_files = [f for f in os.listdir(RULES_DIR) if f.startswith("auto_") and f.endswith(('.mdc', '.md'))]
    # If there are at least 100 auto-generated files, remove oldest to keep only the 99 oldest
    if len(rule_files) >= 100:
        rule_files.sort(key=lambda f: os.path.getmtime(os.path.join(RULES_DIR, f)))
        # Remove files beyond the most recent 99
        for f in rule_files[:-99]:
            try:
                os.remove(os.path.join(RULES_DIR, f))
                logger.info(f"Removed old auto-generated rule: {f}")
            except Exception as e:
                logger.warning(f"Failed to remove rule {f}: {e}")

# Example usage: call cleanup_auto_rules() before generating a new auto rule file

# --- 4. Add retry logic for server startup (example function, not called directly in FastAPI) ---
def start_server():
    """Start the MCP server with retries and port fallback."""
    for attempt in range(3):
        for port in [8000, 8001]:
            if kill_process_on_port(port):
                try:
                    process = subprocess.Popen(
                        ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", str(port)],
                        stdout=open("logs/mcp_server.log", "a"),
                        stderr=subprocess.STDOUT
                    )
                    time.sleep(1)
                    if process.poll() is None:
                        logger.info(f"Server started on port {port}")
                        return
                except Exception as e:
                    logger.error(f"Attempt {attempt+1} on port {port}: {e}")
            time.sleep(2 ** attempt)
    logger.error("Server startup failed after retries")

# --- Rule cleanup in generate_rule_file ---
def generate_rule_file(tool_name, prompt, inputs):
    """Generate a rule file, limiting auto-generated rules to 100 and cleaning up old ones."""
    # Cleanup old auto-generated rules before creating a new one
    cleanup_auto_rules()
    # Directory for rule files
    rules_dir = RULES_DIR
    # Create a unique filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"auto_{timestamp}.mdc"
    path = os.path.join(rules_dir, filename)
    # Compose rule content with a simple Python snippet
    content = (
        "---\n"
        f"description: Auto-generated test rule for prompt '{prompt}'\n"
        "---\n"
        "```python\n"
        "# Auto-generated enforcement logic\n"
        "result = {'status': 'success'}\n"
        "```\n"
    )
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Generated auto rule file: {filename}")
    except Exception as e:
        logger.error(f"Failed to generate auto rule file {filename}: {e}")
    return {'status': 'success', 'filename': filename}

@app.get("/teaching-mode")
async def get_teaching_mode():
    """Check if teaching mode is on."""
    return {"teaching_mode": teaching_mode, "explanation": "teaching mode means you get little explanations for technical terms" if teaching_mode else ""}

def list_log_files_status():
    """List log files and their lock status."""
    import glob
    import psutil
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs'))
    log_files = glob.glob(os.path.join(log_dir, '*.log'))
    status = {}
    for log_file in log_files:
        try:
            with open(log_file, 'a'):
                status[log_file] = 'unlocked'
        except PermissionError:
            status[log_file] = 'locked'
    return status

AVAILABLE_TOOLS.append("list_log_files_status")

@method
def list_log_files_status_rpc() -> Result:
    return Success(list_log_files_status())

# Schedule daily pruning of auto-generated rules with backups
def schedule_prune_rules():
    while True:
        prune_rules()
        time.sleep(86400)  # Wait 24 hours
threading.Thread(target=schedule_prune_rules, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("MCP_SERVER_PORT", 8000))
    # Prevent duplicate servers: if the port is already in use, assume server is running
    if is_port_in_use(port):
        print(f"[MCP] Port {port} is already in use. Assuming another MCP instance is running.")
        print("[MCP] To start a new server, stop the existing one or set MCP_SERVER_PORT to a different port.")
        import sys
        sys.exit(0)
    print(f"[MCP] Starting MCP server on http://localhost:{port}")
    uvicorn.run(
        "scripts.mcp_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 
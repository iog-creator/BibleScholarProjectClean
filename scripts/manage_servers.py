#!/usr/bin/env python3
# NOTE: The primary server management entry points are now start_servers.bat and stop_servers.bat.
# This script is for advanced/manual use and troubleshooting only.
"""
Server Management Script for BibleScholarProject

This script manages the startup and shutdown of all required servers:
- Main Web App (port 5001)
- API Server (port 5000)
- Vector Search Demo (port 5050)
- DSPy Server (port 5003)
- Contextual Insights Server (port 5002)
"""

import os
import sys
import time
import signal
import logging
import subprocess
from typing import Dict, List, Optional
import psutil
import requests
from dotenv import load_dotenv
import json
import datetime
from config.loader import get_config

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/server_management.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Server configurations
SERVERS = {
    'web': {
        'name': 'Web App',
        'script': 'src/web_app.py',
        'port': int(os.getenv('WEB_PORT', 5001)),
        'health_endpoint': '/ping',
        'required': True
    },
    'api': {
        'name': 'API Server',
        'script': 'src/api/api_app.py',
        'port': int(os.getenv('API_PORT', 5000)),
        'health_endpoint': '/ping',
        'required': True
    },
    'vector': {
        'name': 'Vector Search Demo',
        'script': 'src/utils/vector_search_demo.py',
        'port': int(os.getenv('VECTOR_SEARCH_DEMO_PORT', 5050)),
        'health_endpoint': '/ping',
        'required': False
    },
    'insights': {
        'name': 'Contextual Insights Server',
        'script': 'src/api/contextual_insights_api.py',
        'port': int(os.getenv('INSIGHTS_PORT', 5002)),
        'health_endpoint': '/ping',
        'required': False
    }
}

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_server(port: int, endpoint: str = '/ping', timeout: int = 30) -> bool:
    """Wait for server to be ready."""
    config = get_config()
    url = f'http://localhost:{port}{endpoint}'
    start_time = time.time()
    while time.time() - start_time < config.api.api_call_timeout:
        try:
            response = requests.get(url, timeout=config.api.api_call_timeout)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            time.sleep(1)
    return False

def start_server(server_key: str) -> Optional[subprocess.Popen]:
    """Start a server if it's not already running."""
    server = SERVERS[server_key]
    port = server['port']
    
    if is_port_in_use(port):
        logger.info(f"{server['name']} already running on port {port}")
        return None
    
    logger.info(f"Starting {server['name']} on port {port}...")
    
    # Prepare command
    cmd = [sys.executable, server['script']]
    if '--debug' in sys.argv:
        cmd.append('--debug')
    
    # Start server process
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Wait for server to be ready
        if wait_for_server(port, server['health_endpoint']):
            logger.info(f"{server['name']} started successfully")
            return process
        else:
            logger.error(f"Failed to start {server['name']}")
            process.kill()
            return None
    except Exception as e:
        logger.error(f"Error starting {server['name']}: {e}")
        return None

def stop_server(port: int) -> None:
    """Stop a server running on the specified port."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    proc.send_signal(signal.SIGTERM)
                    logger.info(f"Stopped server on port {port}")
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def start_all_servers() -> Dict[str, subprocess.Popen]:
    """Start all required servers."""
    processes = {}
    
    # Start API server first
    api_process = start_server('api')
    if api_process:
        processes['api'] = api_process
    elif SERVERS['api']['required']:
        logger.error("Failed to start required API server")
        return {}
    
    # Start other servers
    for key, server in SERVERS.items():
        if key != 'api':  # Skip API server as it's already handled
            if process := start_server(key):
                processes[key] = process
            elif server['required']:
                logger.error(f"Failed to start required server: {server['name']}")
                stop_all_servers(processes)
                return {}
    
    return processes

def stop_all_servers(processes: Dict[str, subprocess.Popen]) -> None:
    """Stop all running servers."""
    for server_key, process in processes.items():
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        logger.info(f"Stopped {SERVERS[server_key]['name']}")
    
    # Also stop any servers that might be running but not in our processes dict
    for server in SERVERS.values():
        if is_port_in_use(server['port']):
            stop_server(server['port'])

def log_action(log_file, action_message):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {action_message}\n")

def test_mcp_server():
    """Test MCP server for tool discovery and log results."""
    try:
        # Simulate sending a list_tools action to the MCP server
        proc = subprocess.Popen([sys.executable, "scripts/mcp_server.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        request = {"action": "list_tools"}
        stdout, stderr = proc.communicate(json.dumps(request) + "\n", timeout=10)
        log_action("logs/test_results.log", f"MCP list_tools response: {stdout.strip()}")
        if stderr:
            log_action("logs/test_results.log", f"MCP list_tools error: {stderr.strip()}")
        # Test normalize_reference tool
        proc2 = subprocess.Popen([sys.executable, "scripts/mcp_server.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        request2 = {"action": "normalize_reference", "reference": "Jn 3:16"}
        stdout2, stderr2 = proc2.communicate(json.dumps(request2) + "\n", timeout=10)
        log_action("logs/test_results.log", f"MCP normalize_reference response: {stdout2.strip()}")
        if stderr2:
            log_action("logs/test_results.log", f"MCP normalize_reference error: {stderr2.strip()}")
    except Exception as e:
        log_action("logs/test_results.log", f"MCP test exception: {str(e)}")

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Manage BibleScholarProject servers')
    parser.add_argument('action', choices=['start', 'stop', 'restart'],
                      help='Action to perform')
    parser.add_argument('--debug', action='store_true',
                      help='Run servers in debug mode')
    args = parser.parse_args()
    
    if args.action in ['stop', 'restart']:
        stop_all_servers({})  # Stop any running servers
        if args.action == 'stop':
            return
    
    if args.action in ['start', 'restart']:
        processes = start_all_servers()
        if not processes:
            logger.error("Failed to start all required servers")
            sys.exit(1)
        
        try:
            # Keep the script running and monitor server processes
            while True:
                time.sleep(1)
                # Check if any required servers have died
                for key, process in list(processes.items()):
                    if process.poll() is not None:  # Process has terminated
                        if SERVERS[key]['required']:
                            logger.error(f"Required server {SERVERS[key]['name']} has died")
                            stop_all_servers(processes)
                            sys.exit(1)
                        else:
                            logger.warning(f"Optional server {SERVERS[key]['name']} has died")
                            del processes[key]
        except KeyboardInterrupt:
            logger.info("Shutting down servers...")
            stop_all_servers(processes)

if __name__ == '__main__':
    # Example usage: python manage_servers.py test_mcp
    if len(sys.argv) > 1 and sys.argv[1] == "test_mcp":
        test_mcp_server()
    else:
        print("Usage: python manage_servers.py test_mcp") 
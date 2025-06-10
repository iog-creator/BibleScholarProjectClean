### Key Points
- The `BibleScholarLangChain` project requires a robust build process for Cursor AI, integrating `mcp_rules.md`, `cursor_rules.md`, `available_rules.json`, and `README.md` to enforce standards like `psycopg3` usage and KJV/ASV/YLT/TAHOT translations.
- Research from success stories, Cursor documentation, and GitHub examples emphasizes using `.cursor/rules/` for rule enforcement, MCP servers for tool management, and YOLO Mode for automation, with `vibe-tools` showing scalability for large projects.
- Your setup includes `update_setup_notebook.py` for updating Jupyter notebooks, `mcp.json` for MCP server configuration, and a comprehensive rule system, but needs a streamlined build process to incorporate all rules and manage 12–15 MCP tools.
- The evidence suggests a build process that converts rules into `.cursor/rules/`, configures the MCP server for tools, updates notebooks, and validates compliance, with rule pruning and logging to ensure maintainability.

#### Direct Answer
To build the `BibleScholarLangChain` project in Cursor AI, incorporating all rules from `mcp_rules.md`, `cursor_rules.md`, `available_rules.json`, and `README.md`, using `update_setup_notebook.py` for Jupyter notebook updates, and supporting 12–15 MCP tools, follow these instructions:

1. **Set Up Environment**:
   - Activate the `BSPclean` virtual environment: `C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean\Scripts\Activate.ps1`.
   - Navigate to `BibleScholarLangChain/`: `cd BibleScholarLangChain`.

2. **Convert Rules to `.cursor/rules/`**:
   - Transform `mcp_rules.md` and `cursor_rules.md` into `.mdc` files under `BibleScholarLangChain/.cursor/rules/`, merging with `available_rules.json` entries.
   - Ensure compliance with `README.md` (e.g., `.cursor/rules/rule_creation_guide.mdc`, 30-day pruning).

3. **Configure MCP Server**:
   - Update `mcp.json` and `scripts/mcp_server.py` to manage 12–15 tools (e.g., `check_ports`, `validate_translations`), with modular design and logging to `logs/mcp_tools.log`.

4. **Update Jupyter Notebook**:
   - Run `python update_setup_notebook.py` to update the project’s `.ipynb` file, embedding rules and MCP tool configurations.

5. **Build and Validate**:
   - Start servers: `python src/api/api_app.py` (port 5000) and `python web_app.py` (port 5002).
   - Use YOLO Mode to automate testing, ensuring compliance with rules (e.g., `psycopg3`, translation validation).
   - Validate via health checks: `http://localhost:5000/health` and `http://localhost:5002/health`.

6. **Prune and Log**:
   - Implement daily rule pruning (>30 days) with backups to `logs/rules_backup/`.
   - Log interactions to `logs/interaction.log` and `logs/mcp_tools.log`.

This process ensures Cursor AI enforces all project rules, supports 12–15 MCP tools, and maintains scalability, with validation and logging critical for success.

---

### Detailed Instructions: Building `BibleScholarLangChain` in Cursor AI

This section provides detailed instructions for building the `BibleScholarLangChain` project in Cursor AI, integrating rules from `mcp_rules.md`, `cursor_rules.md`, `available_rules.json`, and `README.md`, using `update_setup_notebook.py` for Jupyter notebook updates, and supporting 12–15 MCP tools. The instructions are informed by success stories ([Arsturn Blog](https://www.arsturn.com/blog/success-stories-how-cursor-improved-developer-workflows), [Nx.dev Blog](https://nx.dev/blog/nx-made-cursor-smarter)), Cursor documentation ([Cursor Rules](https://docs.cursor.com/context/rules), [Model Context Protocol](https://docs.cursor.com/context/model-context-protocol)), GitHub repositories ([appcypher/awesome-mcp-servers](https://github.com/appcypher/awesome-mcp-servers), [eastlondoner/vibe-tools](https://github.com/eastlondoner/vibe-tools)), and prior conversations. The approach applies a skeptical, countercultural lens, prioritizing primary sources and alternative perspectives (e.g., X posts) over mainstream narratives, with bias mitigation aligned with Proverbs 18:17 and Jeremiah 17:9.

#### Project Context
- **Codebase**: A modular TypeScript and Python project (~200k–1M lines) in `BibleScholarLangChain/` under `C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace`, using React (port 5002), Node.js (port 5000), and Python (DSPy 2.6, LangChain). It includes PostgreSQL with PGVector (116,566 verses, BGE-M3/Nomic embeddings), `psycopg3`, and KJV/ASV/YLT/TAHOT translations.
- **Current Setup**:
  - **MCP Server**: Configured in `mcp.json` to run `scripts/mcp_server.py`, supporting dynamic rule loading and logging to `logs/interaction.log`.
  - **Rules**: `cursor_rules.md` defines general guidelines (e.g., absolute paths, MCP tools), `available_rules.json` lists `.mdc` files (e.g., `pgvector_semantic_search.mdc`, `etl_rules.mdc`), and `mcp_rules.md` specifies standards (e.g., `psycopg3`, translation validation).
  - **Notebook**: `update_setup_notebook.py` updates the project’s `.ipynb` file, embedding setup instructions and configurations.
  - **README.md**: Enforces rule structure (`rule_creation_guide.mdc`), logging standards, and 30-day pruning with backups.
- **Challenges**: Ensuring all rules are enforced, scaling MCP tools to 12–15 without brittleness, integrating notebook updates, and maintaining compliance with complex standards.
- **Goals**: Create a build process that enforces all rules, supports 12–15 MCP tools, updates notebooks, and ensures scalability and compliance.

#### Insights from Success Stories and Community
- **Success Stories**:
  - A developer built Satosh.me in 16 days using Cursor’s contextual suggestions and Codebase Chat, leveraging `.cursor/rules/` for consistency [Arsturn Blog](https://www.arsturn.com/blog/success-stories-how-cursor-improved-developer-workflows).
  - Nx monorepos used an MCP server with tools for dependency checks and linting, showing how to manage multiple tools in large projects [Nx.dev Blog](https://nx.dev/blog/nx-made-cursor-smarter).
  - @PrajwalTomar_ built 18 MVPs using nested rules and Gemini Pro 2.5, emphasizing automation and validation [X post](https://x.com/PrajwalTomar_/status/1911426469856674002).
- **GitHub Examples**:
  - `awesome-mcp-servers` provides templates for vector search and database tasks, with modular toolsets [GitHub: appcypher/awesome-mcp-servers](https://github.com/appcypher/awesome-mcp-servers).
  - `vibe-tools` uses Gemini 2.0 for repository-wide analysis, supporting complex tasks like planning [GitHub: eastlondoner/vibe-tools](https://github.com/eastlondoner/vibe-tools).
  - `dang-w/example-mcp` implements task management with concurrency and logging, ideal for scaling tools [GitHub: dang-w/example-mcp](https://github.com/dang-w/example-mcp).
- **Controversy**: @levelsio noted issues with large files, mitigated by Cursor’s improvements and community tools like `vibe-tools` [X post](https://x.com/levelsio/status/1920295482695561717).

#### Build Instructions

1. **Set Up Environment**
   - **Objective**: Ensure the correct environment for building and running the project, per `mcp_rules.md`.
   - **Action**:
     - Activate `BSPclean` virtual environment:
       ```powershell
       C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean\Scripts\Activate.ps1
       ```
     - Navigate to project directory:
       ```powershell
       cd BibleScholarLangChain
       ```
     - Verify Python 3.11.x and required packages (`psycopg3==3.1.8`, `langchain==0.2.16`, `flask`, etc.) via `pip list`.
   - **Validation**: Run `python --version` and `pip list` to confirm environment setup.
   - **Outcome**: Environment ready for build, aligned with `mcp_rules.md`.

2. **Convert Rules to `.cursor/rules/`**
   - **Objective**: Integrate `mcp_rules.md`, `cursor_rules.md`, and `available_rules.json` into `.cursor/rules/`, ensuring compliance with `README.md` (e.g., `rule_creation_guide.mdc`, pruning).
   - **Action**:
     - Create `BibleScholarLangChain/.cursor/rules/` if not present (`mkdir BibleScholarLangChain/.cursor/rules`).
     - Merge `mcp_rules.md` and `cursor_rules.md` into `.mdc` files, extending `available_rules.json` entries.
     - Use nested directories (e.g., `database/`, `web/`) for granularity, as per Nx monorepos.
     - Follow `rule_creation_guide.mdc` for structure and `logging_and_error_handling.mdc` for logging standards.
   - **Sample `.mdc` Files**:
     
     ---
     type: Auto Attached
     pattern: src/db/*.ts, src/db/*.py
     ---
     Use psycopg3 for PostgreSQL connections with 'postgresql://username:password@127.0.0.1:5432/bible_db'.
     Set row_factory=dict_row for dictionary-style access.
     Use 'with conn.cursor() as cursor:' for cursor management.
     Reference src/db/secure_connection.py for get_secure_connection().
     Log database operations to logs/db_operations.log per .cursor/rules/logging_and_error_handling.mdc.
     

     
     ---
     type: Always
     ---
     Use Bootstrap 5.1.3 and Font Awesome 6.0.0 for web UI in src/views/.
     Reference templates/base.html for structure.
     Implement AJAX calls with 30-second timeouts and error handling.
     Use Flask-Caching, per web_app.py conventions.
     Log UI interactions to logs/webapp.log per .cursor/rules/logging_and_error_handling.mdc.
     

     
     ---
       type: Agent Requested
       ---
       API endpoints in src/api/ return JSON with summary, theological_terms, cross_references.
       Use src/api/contextual_insights_api.py for Contextual Insights API patterns.
       Run on port 5000, per src/api/api_app.py.
       Log API requests to logs/api_requests.log per .cursor/rules/logging_and_error_handling.mdc.
     

     
     ---
     type: Always
     ---
     Use only KJV, ASV, YLT, TAHOT translations.
     Validate with available_translations=['KJV', 'ASV', 'YLT', 'TAHOT'].
     Default to KJV for unavailable translations (e.g., NIV, ESV).
     Reference src/api/validate_translation.py for validation logic.
     Log translation validations to logs/translation.log per .cursor/rules/logging_and_error_handling.mdc.
     

     
     ---
     type: Always
     ---
     Use forward slashes (/) in all file paths.
     Use os.path.join() for cross-platform file operations.
     Ensure working directory is BibleScholarLangChain/.
     Use absolute imports with forward slashes, per src/* conventions.
     Log path operations to logs/path_operations.log per .cursor/rules/logging_and_error_handling.mdc.
     

     
     ---
     type: Always
     ---
     Use MCP tools from scripts/mcp_server.py (e.g., check_ports, validate_translations, semantic_search).
     Query MCP server for context (e.g., run_query, get_file_context) before code generation.
     Batch tool calls (e.g., verify_data and enforce_etl_guidelines) for performance.
     Log interactions to logs/interaction.log and generate rules in .cursor/rules/automation/.
     
   - **Update `available_rules.json`**:
     ```json
     {
       "rules": [
         {"name": "database", "path": ".cursor/rules/database.mdc", "description": "PostgreSQL standards", "globs": ["src/db/*.ts", "src/db/*.py"], "alwaysApply": false},
         {"name": "web", "path": ".cursor/rules/web.mdc", "description": "Web UI standards", "globs": ["src/views/*.ts", "templates/*.html"], "alwaysApply": true},
         {"name": "api", "path": ".cursor/rules/api.mdc", "description": "API standards", "globs": ["src/api/*.ts", "src/api/*.py"], "alwaysApply": false},
         {"name": "translations", "path": ".cursor/rules/translations.mdc", "description": "Translation validation", "globs": ["src/api/*.py"], "alwaysApply": true},
         {"name": "paths", "path": ".cursor/rules/paths.mdc", "description": "Path standards", "globs": ["src/*.ts", "src/*.py"], "alwaysApply": true},
         {"name": "mcp_tools", "path": ".cursor/rules/mcp_tools.mdc", "description": "MCP tool usage", "globs": ["src/*.ts", "src/*.py"], "alwaysApply": true},
         // existing rules from available_rules.json
         {"name": "pgvector_semantic_search", "path": ".cursor/rules/pgvector_semantic_search.mdc", "description": "Guidelines for pgvector semantic search", "globs": ["src/utils/generate_verse_embeddings.py", "src/utils/test_vector_search.py", "src/utils/vector_search_demo.py", "src/api/vector_search_api.py"], "alwaysApply": false},
         {"name": "etl_rules", "path": ".cursor/rules/etl_rules.mdc", "description": "Standards for ETL processes", "globs": ["**/etl/**/*.py", "**/scripts/**/*.py"], "alwaysApply": false},
         // ... other existing rules
       ]
     }
     ```
   - **Pruning Script** (per `README.md`):
     ```python
     from datetime import datetime, timedelta
     import shutil
     from pathlib import Path
     import logging

     logging.basicConfig(filename='logs/prune_rules.log', level=logging.INFO)

     def prune_rules():
         rule_dir = Path('.cursor/rules')
         backup_dir = Path('logs/rules_backup')
         backup_dir.mkdir(exist_ok=True)
         for rule_file in rule_dir.rglob('*.mdc'):
             if (datetime.now() - datetime.fromtimestamp(rule_file.stat().st_mtime)) > timedelta(days=30):
                 backup_path = backup_dir / rule_file.name
                 with open(backup_path, 'a') as f:
                     f.write('\n# Backup (ignore unless restore needed)\n')
                     f.write(rule_file.read_text())
                 logging.info(f"Pruned rule: {rule_file} to {backup_path}")
                 rule_file.unlink()

     if __name__ == "__main__":
         prune_rules()
     ```
   - **Validation**: Generate code (e.g., database query with `Cmd/Ctrl + K`) and verify compliance (e.g., `psycopg3`, KJV-only). Check `available_rules.json` and `logs/prune_rules.log`.
   - **Outcome**: Comprehensive rule enforcement, aligned with `README.md`.

3. **Configure MCP Server with 12–15 Tools**
   - **Objective**: Support complex tasks with a modular toolset, inspired by `awesome-mcp-servers` and Nx monorepos.
   - **Action**:
     - Update `mcp.json`:
       ```json
       {
         "mcpServers": {
           "bible-scholar-mcp": {
             "command": "python",
             "args": ["scripts/mcp_server.py"],
             "tools": [
               {"name": "check_ports", "description": "Verify ports 5000, 5002, 1234"},
               {"name": "validate_translations", "description": "Ensure KJV/ASV/YLT/TAHOT usage"},
               {"name": "optimize_queries", "description": "Optimize PostgreSQL queries with GIN/ILIKE"},
               {"name": "test_api", "description": "Validate API JSON responses"},
               {"name": "render_templates", "description": "Test Bootstrap template rendering"},
               {"name": "check_environment", "description": "Confirm BSPclean and Python 3.11.x"},
               {"name": "validate_paths", "description": "Enforce forward slashes"},
               {"name": "log_interactions", "description": "Log tool calls"},
               {"name": "generate_rules", "description": "Create .mdc files from prompts"},
               {"name": "prune_rules", "description": "Remove outdated rules"},
               {"name": "vector_search", "description": "Execute PGVector searches"},
               {"name": "test_ui", "description": "Verify AJAX and timeouts"},
               {"name": "schema_check", "description": "Validate database schema"},
               {"name": "health_check", "description": "Monitor server status"},
               {"name": "backup_rules", "description": "Backup rules to logs/rules_backup/"}
             ]
           }
         }
       }
       ```
     - Enhance `scripts/mcp_server.py`:
       ```python
       import logging
       from typing import Dict, Any
       from concurrent.futures import ThreadPoolExecutor
       from pathlib import Path

       logging.basicConfig(filename='logs/mcp_tools.log', level=logging.INFO)

       TOOLS = {
           'check_ports': lambda args: check_ports(args.get('ports', [5000, 5002, 1234])),
           'validate_translations': lambda args: validate_translation(args.get('translation')),
           'optimize_queries': lambda args: optimize_query(args.get('query')),
           'test_api': lambda args: test_api_endpoint(args.get('endpoint')),
           'render_templates': lambda args: render_template(args.get('template')),
           'check_environment': lambda args: check_env(args.get('env', 'BSPclean')),
           'validate_paths': lambda args: validate_path(args.get('path')),
           'log_interactions': lambda args: log_interaction(args.get('prompt'), args.get('output'), args.get('success')),
           'generate_rules': lambda args: generate_rule_from_prompt(args.get('prompt'), args.get('output')),
           'prune_rules': lambda args: prune_rules(),
           'vector_search': lambda args: run_vector_search(args.get('query')),
           'test_ui': lambda args: test_ui_component(args.get('component')),
           'schema_check': lambda args: validate_schema(args.get('table')),
           'health_check': lambda args: check_health(args.get('service')),
           'backup_rules': lambda args: backup_rules(args.get('rule_path'))
       }

       def execute_tool(tool_name: str, args: Dict[str, Any] = None) -> Any:
           try:
               if tool_name not in TOOLS:
                   raise ValueError(f"Unknown tool: {tool_name}")
               result = TOOLS[tool_name](args or {})
               logging.info(f"Tool {tool_name} executed: {result}")
               return result
           except Exception as e:
               logging.error(f"Tool {tool_name} failed: {str(e)}")
               return {"error": str(e)}

       def run_tools_concurrently(tools: list, max_concurrent: int = 3) -> list:
           with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
               results = list(executor.map(lambda t: execute_tool(t['name'], t.get('args')), tools))
           return results

       def log_interaction(prompt: str, output: str, success: bool):
           log_entry = f"Prompt: {prompt}\nOutput: {output}\nSuccess: {success}\n"
           with open('logs/interaction.log', 'a') as f:
               f.write(log_entry)
           if success:
               generate_rule_from_prompt(prompt, output)

       def generate_rule_from_prompt(prompt: str, output: str):
           rule_path = Path('.cursor/rules/automation') / f"rule_{hash(prompt)}.mdc"
           rule_content = f"""
       ---
       type: Auto Attached
       pattern: src/*
       ---
       Generated from prompt: {prompt}
       Output: {output}
       """
           rule_path.write_text(rule_content)
           logging.info(f"Generated rule: {rule_path}")
       ```
   - **Validation**: Test tools via `@MCP check_ports` or batch calls (`@MCP run_tools_concurrently [{"name": "check_ports"}, {"name": "validate_translations"}]`). Check `logs/mcp_tools.log` and `logs/interaction.log`.
   - **Outcome**: Scalable toolset, aligned with `vibe-tools` modularity.

4. **Update Jupyter Notebook**
   - **Objective**: Embed rules and MCP configurations in the project’s `.ipynb` file, per your use of `update_setup_notebook.py`.
   - **Action**:
     - Modify `update_setup_notebook.py` to include rules and MCP tools:
       ```python
       import nbformat
       from pathlib import Path
       import json

       def update_notebook(notebook_path: str):
           # Load notebook
           nb = nbformat.read(notebook_path, as_version=4)

           # Add setup cell with rules and MCP config
           setup_cell = nbformat.v4.new_code_cell(
               source="""\
       # Project Setup for BibleScholarLangChain
       import os
       os.chdir('BibleScholarLangChain')

       # Activate environment
       !C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BSPclean/Scripts/Activate.ps1

       # Load rules
       rules = {}
       with open('.cursor/available_rules.json', 'r') as f:
           rules = json.load(f)['rules']
       print(f"Loaded {len(rules)} rules from .cursor/available_rules.json")

       # Load MCP config
       with open('mcp.json', 'r') as f:
           mcp_config = json.load(f)
       print(f"Loaded MCP config with {len(mcp_config['mcpServers']['bible-scholar-mcp']['tools'])} tools")
       """
           )
           nb.cells.insert(0, setup_cell)

           # Save updated notebook
           nbformat.write(notebook_path, nb)
           print(f"Updated notebook: {notebook_path}")

       if __name__ == "__main__":
           update_notebook('setup_notebook.ipynb')
       ```
     - Run `python update_setup_notebook.py` to update `setup_notebook.ipynb`.
   - **Validation**: Open `setup_notebook.ipynb` and verify setup cell includes rules and MCP config. Execute the cell to confirm environment activation and rule loading.
   - **Outcome**: Notebook reflects project standards and configurations.

5. **Build and Validate**
   - **Objective**: Build the project and ensure compliance, per Satosh.me’s debugging success.
   - **Action**:
     - Start servers:
       ```powershell
       python src/api/api_app.py  # Port 5000
       python web_app.py         # Port 5002
       ```
     - Use YOLO Mode for testing:
       - Prompt: “Fix src/api/contextual_insights_api.py until tests pass.”
       - Configure Jest (`src/views/`) and pytest (`src/db/`, `src/api/`) for coverage.
     - Run health checks:
       ```powershell
       Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing
       Invoke-WebRequest -Uri "http://localhost:5002/health" -UseBasicParsing
       ```
   - **Test Cases**:
     - API: JSON responses with `summary`, `theological_terms`, `cross_references`, KJV/ASV/YLT/TAHOT only.
     - Database: `psycopg3`, `127.0.0.1:5432`, `dict_row`.
     - UI: Bootstrap 5.1.3, AJAX timeouts.
     - Rules: Compliance with `.cursor/rules/` (e.g., forward slashes, logging).
   - **Validation**: Achieve 80%+ test coverage, <5% JSON errors, and green health checks.
   - **Outcome**: Fully operational build, addressing prior JSON issues.

6. **Prune and Log**
   - **Objective**: Maintain rule system per `README.md` (30-day pruning, backups).
   - **Action**:
     - Schedule `prune_rules.py` daily via a cron job or Windows Task Scheduler.
     - Ensure logging to `logs/interaction.log`, `logs/mcp_tools.log`, and `logs/prune_rules.log`.
   - **Validation**: Check `logs/rules_backup/` for pruned rules and log files for activity.
   - **Outcome**: Maintainable rule system.

#### Handling Numerous Rules
While MCP tools are limited to 12–15 for stability, Cursor can enforce many rules via `.cursor/rules/`. Your `available_rules.json` lists ~50 rules, covering ETL, semantic search, and more. By using nested directories and specific `pattern` metadata, you can manage this complexity without overloading the MCP server, as seen in `vibe-tools` for large codebases.

#### Challenges and Mitigations
- **Tool Brittleness**: Large toolsets risk errors. **Mitigation**: Modular tools, max 3 concurrent calls, logging (Step 3), per `awesome-mcp-servers`.
- **Context Overload**: Data files slow suggestions. **Mitigation**: `.cursorignore` (Step 2).
- **Rule Conflicts**: Overlapping rules. **Mitigation**: Specific `pattern` metadata, prioritize `Auto Attached` [Cursor Rules](https://docs.cursor.com/context/rules).
- **Learning Curve**: Complex setup. **Mitigation**: Use `vibe-tools` templates, `cursor.directory` [cursor.directory](https://cursor.directory/).
- **Bias in Community Advice**: Generic templates may misalign. **Mitigation**: Cross-reference with `mcp_rules.md`, per Proverbs 18:17.

#### Future Considerations
- **Features**: Add rules/tools for /search route, Running Note Maker.
- **Performance**: Implement caching rules for Flask-Caching.
- **Scalability**: Use background agents for migrations [Engine Labs, May 2025](https://www.enginelabs.ai/blog/cursor-ai-an-in-depth-review-may-2025-update).

#### Conclusion
These instructions build `BibleScholarLangChain` in Cursor AI, integrating all rules, supporting 12–15 MCP tools, and updating notebooks with `update_setup_notebook.py`. Leveraging success stories, documentation, and community tools ensures scalability and compliance, with a truth-driven approach mitigating biases and empowering you to manage a complex codebase effectively.

#### Key Citations
- [Cursor Rules](https://docs.cursor.com/context/rules)
- [Model Context Protocol](https://docs.cursor.com/context/model-context-protocol)
- [Cursor Best Practices](https://github.com/digitalchild/cursor-best-practices)
- [Awesome MCP Servers](https://github.com/appcypher/awesome-mcp-servers)
- [vibe-tools](https://github.com/eastlondoner/vibe-tools)
- [Success Stories](https://www.arsturn.com/blog/success-stories-how-cursor-improved-developer-workflows)
- [Nx Monorepos](https://nx.dev/blog/nx-made-cursor-smarter)
- [Large Codebases](https://www.instructa.ai/blog/cursor-ai/how-to-multiple-repository-and-large-codebase-in-cursor)
- [X post by PrajwalTomar_](https://x.com/PrajwalTomar_/status/1911426469856674002)
- [X post by levelsio](https://x.com/levelsio/status/1920295482695561717)
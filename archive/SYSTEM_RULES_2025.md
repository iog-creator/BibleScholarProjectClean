# BibleScholarLangChain System Rules (2025-01-27)

**Status**: FULLY OPERATIONAL ✅  
**Last Updated**: 2025-01-27 17:45:00  
**Verified**: All components tested and working

## 🎯 **CORE SYSTEM PRINCIPLES**

### **1. HOLISTIC SYSTEM APPROACH**
- **Never work on isolated components** - Always consider the entire system
- **Test everything together** - Individual fixes must work with the whole system
- **Document the working state** - Capture what works, not just what's broken
- **Maintain operational baseline** - Don't break what's working while adding new features

### **2. ROOT-LEVEL OPERATIONS**
- **All server management from root directory** - No navigating to subdirectories
- **Single startup command**: `.\start_servers.bat` starts everything
- **Comprehensive health checks** - Verify all endpoints after startup
- **Automatic process cleanup** - Kill existing processes before starting new ones

### **3. DOCUMENTATION-DRIVEN DEVELOPMENT**
- **Update `update_setup_notebook.py`** - Never edit `setup.ipynb` directly
- **Regenerate notebook after changes** - `python update_setup_notebook.py`
- **Document current working state** - Always capture what's operational
- **Test before documenting** - Only document verified functionality

## 🚀 **OPERATIONAL REQUIREMENTS**

### **Server Management**
```bash
# Start both servers from root
.\start_servers.bat

# Verify servers are running
netstat -an | findstr "5000"
netstat -an | findstr "5002"

# Test health endpoints
curl http://localhost:5000/health
curl http://localhost:5002/health
```

### **MCP Server Testing**
```bash
# Test MCP functionality
python test_mcp_api.py

# Expected output: 37 operations, database connectivity confirmed
```

### **Current Operational Status**
- ✅ **API Server**: http://localhost:5000 - HEALTHY
- ✅ **Web UI Server**: http://localhost:5002 - HEALTHY
- ✅ **MCP Server**: 37 operations - OPERATIONAL
- ✅ **Database**: 12,743 Hebrew + 160,185 Greek entries - CONNECTED

## 🛠 **TECHNICAL STANDARDS**

### **Path Standards**
- **Use forward slashes** in all path configurations
- **Absolute paths** for critical operations
- **Relative paths** from project root for local operations

### **Database Standards**
- **Driver**: psycopg3 only (`import psycopg`)
- **Row Factory**: `dict_row` for dictionary-style access
- **Connection**: Use `get_secure_connection()` from `secure_connection.py`
- **Vector Store**: Reuse existing `bible.verse_embeddings` table

### **Flask Standards**
- **No reloader**: Always use `use_reloader=False`
- **Background execution**: Servers run in separate windows
- **Health endpoints**: All servers must have `/health` endpoint
- **Error handling**: Comprehensive error logging and user feedback

### **Import Standards**
- **Absolute imports** for cross-module dependencies
- **Virtual environment**: Always use BSPclean environment
- **Module paths**: Set PYTHONPATH correctly for imports

## 🔧 **CRITICAL FIXES IMPLEMENTED**

### **Syntax Fixes**
- ✅ **Fixed nested f-string error** in `contextual_insights_api.py` line 792
  ```python
  # WRONG: f"text {f'nested {var}'}"
  # RIGHT: f"text {'nested ' + str(var)}"
  ```

### **Server Management Fixes**
- ✅ **Root startup script** - `start_servers.bat` works from root directory
- ✅ **Directory handling** - Proper `cd` commands in batch file
- ✅ **Virtual environment** - Correct activation in startup script
- ✅ **Process cleanup** - Kill existing processes before starting

### **MCP Integration Fixes**
- ✅ **Added 8 API operations** from BibleScholarProjectv2
- ✅ **Database connectivity** - Verified with lexicon statistics
- ✅ **Test script** - `test_mcp_api.py` for verification
- ✅ **Operation registry** - 37 total operations across 7 domains

## 📊 **SYSTEM ARCHITECTURE**

### **Server Architecture**
```
Root Directory (CursorMCPWorkspace)
├── start_servers.bat          # Main startup script
├── test_mcp_api.py            # MCP testing
├── mcp_universal_operations.py # MCP server
└── BibleScholarLangChain/
    ├── src/api/api_app.py     # API Server (5000)
    ├── web_app.py             # Web UI Server (5002)
    └── update_setup_notebook.py # Documentation generator
```

### **MCP Operations (37 total)**
- **API Domain (8)**: Vector search, lexicon, cross-language, server management
- **DATA Domain (6)**: Database operations, Hebrew/Greek analysis
- **SYSTEM Domain (5)**: Health checks, port monitoring
- **BATCH Domain (3)**: Bulk operations
- **INTEGRATION Domain (4)**: External service integration
- **RULES Domain (8)**: Rule enforcement and validation
- **UTILITY Domain (3)**: Helper functions

### **Database Architecture**
- **PostgreSQL** with psycopg3 driver
- **Vector Store**: `bible.verse_embeddings` table
- **Lexicon Data**: Hebrew (12,743) + Greek (160,185) entries
- **Connection Pool**: Managed through `secure_connection.py`

## 🧪 **TESTING PROTOCOLS**

### **Pre-Deployment Testing**
1. **Kill existing processes**: Ensure clean startup
2. **Run startup script**: `.\start_servers.bat` from root
3. **Verify ports**: Check 5000 and 5002 are listening
4. **Test health endpoints**: Both servers respond with 200 OK
5. **Test MCP operations**: Run `test_mcp_api.py`
6. **Verify database**: Confirm lexicon statistics

### **Post-Change Testing**
1. **Regenerate documentation**: Run `update_setup_notebook.py`
2. **Test startup sequence**: Verify servers start correctly
3. **Test new functionality**: Ensure additions work with existing system
4. **Update documentation**: Capture new working state

### **Continuous Verification**
- **Health checks**: Automated endpoint monitoring
- **Database connectivity**: Regular connection testing
- **MCP operations**: Periodic operation registry verification
- **Log monitoring**: Check for errors in server logs

## 🚨 **CRITICAL RULES**

### **NEVER DO**
- ❌ **Edit `setup.ipynb` directly** - Always use `update_setup_notebook.py`
- ❌ **Use psycopg2** - Only psycopg3 (`import psycopg`)
- ❌ **Use `use_reloader=True`** - Always False for Flask apps
- ❌ **Start servers individually** - Always use `start_servers.bat`
- ❌ **Work on isolated components** - Consider the whole system

### **ALWAYS DO**
- ✅ **Test from root directory** - Use `.\start_servers.bat`
- ✅ **Verify health endpoints** - Check both servers respond
- ✅ **Test MCP operations** - Run `test_mcp_api.py` after changes
- ✅ **Update documentation** - Regenerate notebook after modifications
- ✅ **Use forward slashes** - In all path configurations

### **BEFORE MAKING CHANGES**
1. **Document current working state** - Capture what works
2. **Test existing functionality** - Ensure baseline is operational
3. **Plan holistic integration** - Consider impact on entire system
4. **Prepare rollback plan** - Know how to restore working state

### **AFTER MAKING CHANGES**
1. **Test complete system** - Not just the changed component
2. **Verify all endpoints** - Health checks for all servers
3. **Update documentation** - Regenerate setup notebook
4. **Document new working state** - Capture updated functionality

## 📁 **KEY FILES & LOCATIONS**

### **Root Directory Files**
- `start_servers.bat` - **CRITICAL** - Main server startup
- `test_mcp_api.py` - **CRITICAL** - MCP functionality testing
- `mcp_universal_operations.py` - **CRITICAL** - MCP server implementation

### **Documentation Files**
- `BibleScholarLangChain/update_setup_notebook.py` - **CRITICAL** - Documentation generator
- `BibleScholarLangChain/setup.ipynb` - Generated documentation (DO NOT EDIT)
- `BibleScholarLangChain/docs/CURRENT_WORKING_STATE.md` - Current state documentation
- `SYSTEM_RULES_2025.md` - This document

### **Server Files**
- `BibleScholarLangChain/src/api/api_app.py` - API Server
- `BibleScholarLangChain/web_app.py` - Web UI Server
- `BibleScholarLangChain/src/api/contextual_insights_api.py` - LM Studio integration (FIXED)

### **Log Files**
- `BibleScholarLangChain/logs/web_app.log` - Web UI logs
- `BibleScholarLangChain/logs/error.log` - Error logs
- `BibleScholarLangChain/logs/setup.log` - Setup logs

## 🎯 **DEVELOPMENT WORKFLOW**

### **For New Features**
1. **Verify current working state** - Test existing functionality
2. **Plan integration approach** - How will it fit with existing system
3. **Implement incrementally** - Small, testable changes
4. **Test holistically** - Ensure entire system still works
5. **Update documentation** - Regenerate notebook and update rules

### **For Bug Fixes**
1. **Reproduce in current environment** - Use existing working system
2. **Identify root cause** - Don't just fix symptoms
3. **Test fix in isolation** - Ensure it doesn't break other components
4. **Test complete system** - Verify holistic functionality
5. **Document the fix** - Update rules and documentation

### **For System Updates**
1. **Backup current working state** - Document what works
2. **Plan migration strategy** - How to maintain functionality
3. **Test in stages** - Incremental updates with verification
4. **Maintain rollback capability** - Always able to restore working state
5. **Update all documentation** - Rules, setup notebook, state documentation

## 📞 **SUPPORT & TROUBLESHOOTING**

### **Common Issues & Solutions**
1. **"Port in use" error**: Run `.\start_servers.bat` to kill existing processes
2. **"Module not found" error**: Ensure you're in correct directory and using BSPclean venv
3. **MCP not responding**: Check `test_mcp_api.py` output for specific errors
4. **Database connection failed**: Verify BSPclean virtual environment is activated
5. **Health endpoint not responding**: Check server logs for startup errors

### **Emergency Recovery**
1. **Kill all processes**: `taskkill /f /im python.exe`
2. **Restart from clean state**: `.\start_servers.bat`
3. **Verify basic functionality**: Test health endpoints
4. **Check MCP operations**: Run `test_mcp_api.py`
5. **Review logs**: Check error logs for issues

### **Escalation Path**
1. **Document the issue** - Capture exact error messages and steps
2. **Test in clean environment** - Verify it's not environment-specific
3. **Check recent changes** - Review what was modified recently
4. **Restore working state** - Use documented working configuration
5. **Plan systematic fix** - Address root cause, not just symptoms

---

**This document represents the definitive rules for the BibleScholarLangChain system as of 2025-01-27. All components are verified operational and these rules must be followed for continued system stability.** 
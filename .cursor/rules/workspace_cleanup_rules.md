# Workspace Cleanup and Organization Rules

## 🎯 **PRIMARY GOAL**
Maintain a clean, organized workspace with **ONE ACTIVE PROJECT** and clear file hierarchy to prevent confusion and duplicate file issues.

## 📁 **ACTIVE PROJECT STRUCTURE**
```
CursorMCPWorkspace/
├── BibleScholarLangChain/          # 🟢 ACTIVE PROJECT (ONLY ONE)
│   ├── src/                        # Source code
│   ├── scripts/                    # Utility scripts
│   ├── tests/                      # Test files
│   ├── docs/                       # Documentation
│   └── mcp_universal_operations.py # MCP operations (SINGLE SOURCE)
├── scripts/                        # 🟢 GLOBAL SCRIPTS (shared utilities)
├── .cursor/                        # 🟢 CURSOR CONFIG
├── archive/                        # 🔴 ARCHIVED PROJECTS (read-only)
└── logs/                          # 🟢 LOGS
```

## 🚫 **IMMEDIATE CLEANUP TARGETS**
These directories should be moved to archive:

### **Duplicate Projects (ARCHIVE IMMEDIATELY)**
- `BibleScholarProjectv2/` → `archive/BibleScholarProjectv2/`
- `BibleScholarProjectClean/` → `archive/BibleScholarProjectClean/`
- `archive_workspace/` → `archive/archive_workspace/`

### **KEEP IN WORKSPACE (DO NOT ARCHIVE)**
- `BSPclean/` → **PYTHON VIRTUAL ENVIRONMENT** (Required for MCP server)

### **Temporary/Cache Directories (DELETE)**
- `.ipynb_checkpoints/`
- `.pytest_cache/`
- `.benchmarks/`
- `__pycache__/` (all instances)

## 📋 **FILE DEDUPLICATION RULES**

### **MCP Operations (CRITICAL)**
- ✅ **SINGLE SOURCE**: `BibleScholarLangChain/mcp_universal_operations.py`
- ❌ **REMOVE**: `scripts/mcp_universal_operations.py`
- ❌ **REMOVE**: Any other copies in archived projects

### **MCP Server (CRITICAL)**
- ✅ **SINGLE SOURCE**: `scripts/mcp_server_refactored.py`
- ❌ **REMOVE**: `scripts/mcp_server.py` (old version)
- ❌ **REMOVE**: Any other MCP server files

### **Configuration Files**
- ✅ **SINGLE SOURCE**: `.cursor/mcp.json`
- ✅ **SINGLE SOURCE**: `requirements.txt` (root level)
- ❌ **REMOVE**: Duplicate requirements files in subprojects

## 🔧 **CLEANUP AUTOMATION SCRIPT**

```bash
# Phase 1: Archive duplicate projects (KEEP BSPclean - it's the Python venv!)
mkdir -p archive/
mv BibleScholarProjectv2/ archive/
mv BibleScholarProjectClean/ archive/
mv archive_workspace/ archive/
# DO NOT MOVE BSPclean/ - it's the Python virtual environment!

# Phase 2: Remove cache directories
rm -rf .ipynb_checkpoints/
rm -rf .pytest_cache/
rm -rf .benchmarks/
find . -name "__pycache__" -type d -exec rm -rf {} +

# Phase 3: Consolidate MCP files
rm scripts/mcp_universal_operations.py
rm scripts/mcp_server.py

# Phase 4: Update MCP config to use consolidated files
# Update .cursor/mcp.json to point to correct paths
```

## 🛡️ **PREVENTION RULES**

### **Before Creating New Files**
1. ✅ Check if file already exists in active project
2. ✅ Use existing file or create in correct location
3. ❌ Never create duplicate implementations

### **Before Adding Dependencies**
1. ✅ Add to root `requirements.txt`
2. ❌ Never create project-specific requirements files

### **Before Creating New Projects**
1. ✅ Archive old projects first
2. ✅ Maintain single active project structure
3. ❌ Never have multiple active Bible Scholar projects

## 🎯 **ACTIVE PROJECT FOCUS**
- **PRIMARY**: `BibleScholarLangChain/` (LangChain-based implementation)
- **SCRIPTS**: `scripts/` (shared utilities)
- **CONFIG**: `.cursor/` (Cursor configuration)
- **ARCHIVE**: `archive/` (historical projects, read-only)

## 📊 **SUCCESS METRICS**
- ✅ Single `mcp_universal_operations.py` file
- ✅ Single active Bible Scholar project
- ✅ No duplicate configuration files
- ✅ Clear separation between active and archived code
- ✅ MCP server works without path confusion

## 🚨 **ENFORCEMENT**
- Before any major changes, run cleanup validation
- Archive old projects before starting new ones
- Maintain single source of truth for all implementations
- Use consistent import paths and file locations

---
**Type**: always  
**Description**: Workspace organization and cleanup rules to prevent file duplication  
**Globs**: `**/*`  
**AlwaysApply**: true 
# Fix PowerShell Extension Yellow Warning

## 🚨 **ISSUE: PowerShell Extension Yellow State**
The PowerShell extension in Cursor is showing a yellow warning state after restart, likely due to configuration conflicts or cached state.

## ✅ **SOLUTION: Restart PowerShell Extension**

### **Method 1: Command Palette (Recommended)**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `PowerShell: Restart Session`
3. Select and execute the command
4. The yellow warning should disappear
5. New terminal will auto-activate BSPclean venv

### **Method 2: Kill Terminal Process**
1. In Cursor, go to Terminal menu
2. Select "Kill All Terminals" or close the terminal panel
3. Open a new terminal (`Ctrl+`` ` or Terminal > New Terminal)
4. Should automatically show `(BSPclean) PS>` prompt

### **Method 3: Reload Cursor Window**
1. Press `Ctrl+Shift+P`
2. Type: `Developer: Reload Window`
3. This will reload the entire Cursor window
4. Open new terminal - should auto-activate BSPclean

## ✅ **AUTOMATIC VENV ACTIVATION CONFIGURED**

The setup script has configured:
- **Workspace PowerShell profile**: Auto-activates BSPclean venv
- **Cursor settings**: Default Python interpreter points to BSPclean
- **Terminal configuration**: Always starts in workspace root with venv

### **Expected Behavior After Fix**
```powershell
# When you open a new terminal, you should see:
🔧 Auto-activating BSPclean virtual environment...
✅ BSPclean virtual environment activated
Python: Python 3.12.3
Location: C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean\Scripts\python.exe
(BSPclean) PS C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace>
```

## 🎯 **VERIFICATION**
After restarting the PowerShell extension:
- [ ] Yellow warning gone
- [ ] Terminal prompt shows `(BSPclean) PS>`
- [ ] Python version: `python --version` shows `Python 3.12.3`
- [ ] Python path: `python -c "import sys; print(sys.executable)"` shows BSPclean path
- [ ] MCP operations work: `python -c "from mcp_universal_operations import universal_router; print('Operations:', len(universal_router.operation_registry))"`

## 🚨 **IF ISSUES PERSIST**
If the yellow warning continues or auto-activation doesn't work:
1. Check `.vscode/settings.json` was created properly
2. Verify `workspace_profile.ps1` exists
3. Try reloading the entire Cursor window
4. Check PowerShell execution policy: `Get-ExecutionPolicy`

The key is **killing and restarting the PowerShell extension** to clear the cached problematic state and load the new configuration. 
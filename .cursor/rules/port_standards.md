# Port Standards

## Standardized Port Assignments (Increments of 100)

**Active Ports:**
- **5200** - API Server (`test_api_simple.py`, `api_app.py`)
- **5300** - Web Application (`web_app.py`)

**Reserved Ports:**
- **5400** - Vector Search Service (future)
- **5500** - Analytics Service (future)
- **5600** - Export Service (future)
- **5700** - Admin Interface (future)

**External Services:**
- **1234** - LM Studio (external)
- **5432** - PostgreSQL Database (external)

## Configuration Files Updated:
- `test_api_simple.py` → Port 5200
- `BibleScholarLangChain/web_app.py` → Port 5300
- `BibleScholarLangChain/src/api/api_app.py` → Port 5200

## Access URLs:
- API Server: `http://localhost:5200`
- Web App: `http://localhost:5300`
- Contextual Insights UI: `http://localhost:5300/contextual-insights`

## Rule Type:
- **Type**: Always Apply
- **Priority**: High
- **Enforcement**: All new services must use the next available increment of 100 
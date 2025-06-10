# Contextual Insights Feature

> **Note:** This documentation is governed by the project's single source of truth rule. Always check the main README.md and .cursor/rules/single-source-of-truth.mdc for the latest standards and onboarding instructions.

---

## Purpose
The Contextual Insights feature provides rich, model-generated insights for Bible verses, including summaries, theological terms, cross-references, historical context, original language notes, and related entities. It is accessible via both a web page and a REST API.

---

## User Workflow
1. **Web UI**: Users visit the Contextual Insights page (http://localhost:5001/contextual-insights), enter a verse reference (e.g., John 3:16), and receive structured insights.
2. **API**: Programmatic access is available via a POST request to the API server (http://localhost:5000/api/contextual_insights/insights).

---

## Web UI
- **URL**: http://localhost:5001/contextual-insights
- **Template**: `templates/contextual_insights.html`
- **Features**:
  - Input form for verse reference and translation
  - Displays summary, theological terms, cross-references, historical context, original language notes, and related entities
  - Handles long model response times (timeout: 120 seconds)
  - Error handling for missing or malformed insights

---

## API Endpoints
- **POST /api/contextual_insights/insights** (Port 5000)
  - **Request JSON**:
    ```json
    {
      "type": "verse",
      "reference": "John 3:16",
      "translation": "KJV"
    }
    ```
  - **Response JSON** (example):
    ```json
    {
      "insights": {
        "summary": "John 3:16 emphasizes God's love...",
        "theological_terms": {"Grace": "...", ...},
        "cross_references": [{"reference": "John 1:29", ...}, ...],
        "historical_context": "...",
        "original_language_notes": [{"word": "ἀγάπη", ...}, ...],
        "related_entities": {"people": [...], "places": [...]}
      }
    }
    ```
  - **Error Handling**: Returns error JSON if the model is unavailable or times out.

---

## Configuration
- **Environment Variables**:
  - `HUGGINGFACE_API_KEY` (if using remote models)
  - `LM_STUDIO_API_URL`, `LM_STUDIO_CHAT_MODEL` (for local LM Studio integration)
  - See `.env.example` for all required variables
- **Timeout**: The web app allows up to 120 seconds for model responses

---

## Troubleshooting
- **Model Not Responding**: Ensure LM Studio is running and the correct model is loaded
- **API 404 or Connection Refused**: Verify all servers are running (see `start_servers.bat`)
- **Web UI Loads but No Insights**: Check logs for errors, ensure API and Contextual Insights servers are healthy (`/health` endpoints)
- **Long Response Times**: Model inference may take up to 2 minutes; increase timeout if needed
- **Malformed Output**: The backend uses robust JSON extraction; check logs for parsing errors
- **GPU Overload or Multiple LM Studio Jobs**: The backend now serializes all Contextual Insights model jobs (see `src/dspy_programs/contextual_insights_program.py`). Only one job runs at a time; if you submit a new request while another is running, it will wait for the first to finish. This prevents GPU overload and multiple concurrent LM Studio jobs.

---

## Usage Examples
- **Web UI**: Go to http://localhost:5001/contextual-insights, enter `John 3:16`, select translation, and submit
- **API (PowerShell)**:
  ```powershell
  Invoke-RestMethod -Uri "http://localhost:5000/api/contextual_insights/insights" -Method Post -ContentType "application/json" -Body '{"type": "verse", "reference": "John 3:16", "translation": "KJV"}'
  ```
- **API (curl)**:
  ```sh
  curl -X POST http://localhost:5000/api/contextual_insights/insights \
    -H "Content-Type: application/json" \
    -d '{"type": "verse", "reference": "John 3:16", "translation": "KJV"}'
  ```

---

## Integration & Related Docs
- **Web App**: `src/web_app.py` (handles UI and API proxying)
- **API Server**: `src/api/api_app.py` (serves the API endpoint)
- **Contextual Insights Program**: `src/dspy_programs/contextual_insights_program.py` (model logic)
- **README.md**: Canonical onboarding and standards
- **See Also**:
  - [Semantic Search](./semantic_search.md)
  - [Theological Terms](./theological_terms.md)
  - [Testing Framework](../guides/testing_framework.md)
  - [Data Verification Guide](../guides/data_verification.md)

---

## Maintenance
- Update this doc and the README if the Contextual Insights feature, API, or UI changes
- Follow the [single source of truth rule](../../.cursor/rules/single-source-of-truth.mdc)

# Compliance Note
All model and API settings must be loaded from config and `.env`. No hardcoded values are permitted. Update this documentation if the config changes. 
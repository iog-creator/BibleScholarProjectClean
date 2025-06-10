# System Architecture Reference

This document provides a comprehensive reference of the BibleScholarProject's system architecture, components, and organization.

## Overview

The BibleScholarProject follows a layered architecture:

1. **Data Layer**: PostgreSQL database containing lexicons, Bible texts, and relationships
2. **ETL Layer**: Python scripts for extracting, transforming, and loading STEPBible data
3. **API Layer**: REST endpoints for accessing the data
4. **Presentation Layer**: Web interface for exploring the data

## Directory Structure

The project is organized into the following directories:

```
BibleScholarProject/
├── config/                 # Configuration files
├── data/                   # Data files
│   ├── processed/          # Processed data
│   └── raw/                # Original data from STEPBible
├── docs/                   # Project documentation
│   ├── features/           # Feature documentation
│   ├── guides/             # How-to guides and tutorials
│   └── reference/          # Reference documentation
├── logs/                   # Log files
├── src/                    # Source code
│   ├── api/                # API endpoints and controllers
│   ├── database/           # Database connection and operations
│   ├── etl/                # ETL scripts for data processing
│   │   ├── morphology/     # Morphology code processing
│   │   └── names/          # Proper names processing
│   ├── tvtms/              # Versification mapping code
│   └── utils/              # Utility functions and helpers
├── templates/              # HTML templates for the web interface
└── tests/                  # Test files
    ├── data/               # Test data files
    ├── integration/        # Integration tests
    └── unit/               # Unit tests
```

## Database Schema

The database schema includes the following key tables:

### Lexicon Tables
- **hebrew_entries**: Hebrew lexicon entries from TBESH
- **greek_entries**: Greek lexicon entries from TBESG
- **word_relationships**: Relationships between words

### Tagged Text Tables
- **verses**: Bible verses with metadata
- **greek_nt_words**: Individual Greek words from the NT
- **hebrew_ot_words**: Individual Hebrew words from the OT

### Morphology Tables
- **hebrew_morphology_codes**: Hebrew morphology code explanations
- **greek_morphology_codes**: Greek morphology code explanations

### Proper Names Tables
- **proper_names**: Biblical proper names
- **proper_name_forms**: Forms of proper names in original languages
- **proper_name_references**: Biblical references for proper names

### Arabic Bible Tables
- **arabic_verses**: Arabic Bible verses
- **arabic_words**: Individual Arabic words with tagging

### Versification Tables
- **versification_mappings**: Maps between different versification traditions

### Semantic Search Tables
- **verse_embeddings**: Vector embeddings for semantic search

For complete database schema details, see [Database Schema](DATABASE_SCHEMA.md).

## ETL Process

The ETL (Extract, Transform, Load) process is handled by scripts in the `src/etl/` directory:

### Key ETL Scripts

1. **etl_lexicons.py**: Processes Hebrew and Greek lexicons
2. **etl_greek_nt.py**: Processes Greek New Testament
3. **etl_hebrew_ot.py**: Processes Hebrew Old Testament
4. **etl_morphology/**: Processes morphology codes
5. **etl_names/etl_proper_names.py**: Processes proper names
6. **etl_arabic_bible.py**: Processes Arabic Bible
7. **tvtms/process_tvtms.py**: Processes versification mappings
8. **fix_hebrew_strongs_ids.py**: Fixes Hebrew Strong's IDs

For detailed ETL process documentation, see [ETL Pipeline](../features/etl_pipeline.md).

## API Endpoints

The API is organized into the following endpoint groups:

### Lexicon API
- Endpoints for accessing Hebrew and Greek lexicon entries

### Bible Text API
- Endpoints for accessing verses and tagged words

### Morphology API
- Endpoints for accessing morphology code explanations

### Proper Names API
- Endpoints for accessing biblical proper names and references

### Semantic Search API
- Endpoints for vector-based semantic search

### Bible QA API
- Endpoints for answering Bible questions using AI models
- Includes the optimized Bible QA system using non-synthetic training data

For complete API documentation, see [API Reference](API_REFERENCE.md).

## Web Interface

The web interface includes the following key pages:

- **Home page**: Search interface and overview
- **Lexicon entry**: Details of a lexicon entry
- **Verse detail**: Verse with tagged words and analysis
- **Morphology detail**: Explanation of morphology codes
- **Proper name detail**: Details of a proper name with references
- **Semantic search**: Interface for semantic search

## Testing Framework

The testing framework includes:

- **Unit tests**: For testing individual components
- **Integration tests**: For testing component interactions
- **Theological term tests**: For validating theological term integrity

For detailed testing documentation, see [Testing Framework](../guides/testing_framework.md).

## Data Verification

The system includes comprehensive data verification:

- **Statistical verification**: Ensures expected counts match actual data
- **Theological term verification**: Tests accurate representation of key theological terms
- **Critical passage verification**: Verifies the integrity of theologically significant passages
- **Linguistic verification**: Ensures proper linguistic representation

For detailed verification documentation, see [Data Verification](../guides/data_verification.md).

## Configuration

The BibleScholarProjectv2 uses a **centralized, single source of truth** for all non-sensitive application configuration: `config/config.json`. This file is located at the project root and contains settings for:

*   **`models`**: Definitions, parameters, and prompt formats for all LLM, embedding, and reranker models.
*   **`api`**: URLs and timeouts for all internal and external API endpoints (e.g., LM Studio, Vector Search, Database).
*   **`features`**: Feature flags and other application-wide settings (e.g., `enable_thinking`).
*   **`vector_search`**: Parameters and settings specific to vector search functionality.
*   **`testing`**: Configuration related to testing and validation.
*   **`ui`**: Settings for the user interface.
*   **`defaults`**: Default values for model selection, translation, etc.

The configuration is loaded at runtime using the `get_config()` utility from `config/loader.py` and validated using Pydantic models defined in `config/models.py`. This ensures type safety and consistency.

**Environment Variables (`.env`)**

The `.env` file, located at the project root, is now used minimally and strictly for **secrets and necessary environment-specific overrides**. It should **not** contain model parameters or other non-sensitive settings that belong in `config.json`.

Key variables that may be present in `.env`:

*   `CONFIG_PATH`: Optional path to the `config.json` file (defaults to `./config/config.json`).
*   Database Credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`, etc.): Sensitive database connection details.
*   API Keys or Secrets (`API_KEY`, `SECRET_KEY`, etc.): Any sensitive keys required by the application.
*   `API_BASE_URL`: Base URL for internal APIs (used in the web app to connect to the API server).

## Config-Driven Embedding and Reranker Model Selection

The BibleScholarProjectv2 uses a single source of truth for all model, prompt, and parameter settings, including LLM, embedding, and reranker models. These are defined in `config/config.json` and validated at runtime using Pydantic models.

### How It Works
- All code that calls an LLM, embedding, or reranker model loads the relevant settings from `config/config.json` using the `get_config()` utility from `config/loader.py`.
- This includes model names, prompt templates, and any model-specific parameters.
- No model names or parameters are hardcoded or loaded from environment variables.

### Example Config Section
```json
"vector_search": {
  "embedding_model": "bge-m3",
  "embedding_prompt": "Represent this sentence for searching relevant passages: {text}",
  "reranker_model": "bge-reranker-base",
  "reranker_prompt": "Query: {query}\nDocument: {document}\nRelevant:",
  ...
}
```

### Runtime Loading Pattern
```python
from config.loader import get_config
config = get_config()
embedding_model = config.vector_search.embedding_model
reranker_model = config.vector_search.reranker_model
embedding_prompt = config.vector_search.embedding_prompt
reranker_prompt = config.vector_search.reranker_prompt
```

This ensures that any change to the config file is immediately reflected in all model calls after a restart, maintaining consistency and simplifying maintenance.

## Related Documentation

- [ETL Pipeline](../features/etl_pipeline.md)
- [Semantic Search](../features/semantic_search.md)
- [Bible Translations](../features/bible_translations.md)
- [Theological Terms](../features/theological_terms.md)
- [Optimized Bible QA](../features/optimized_bible_qa.md)
- [Database Schema](DATABASE_SCHEMA.md)
- [API Reference](API_REFERENCE.md)
- [Testing Framework](../guides/testing_framework.md)
- [Data Verification](../guides/data_verification.md)

## Modification History

| Date | Author | Description |
|------|--------|-------------|
| 2025-06-10 | Documentation Team | Created system architecture reference document |

### Server Architecture
- **All Servers**: Standardized with UTF-8 logging, PYTHONPATH=src, port conflict handling, health endpoints (/ping).
- **MCP Server**: Dynamic rule execution, cleanup (100-file cap), and watchdog reloading.
- **Web App**: Enhanced with /search route for Contextual Insights integration and original_language_notes UI display.
+ **Contextual Insights Server**: 
+  - *Logging*: Stdout and stderr directed to `logs/contextual_insights.log`; program-specific debug and inference logs are written to `logs/contextual_insights_program.log`.

### Robust Server Management (May 2025)
All servers now use:
- UTF-8 log encoding and log directory checks
- Consistent log file naming and truncation
- Health checks and port polling for all services
- Robust batch and Python scripts for startup/shutdown
- Unified log tailing and startup summaries

**Enforced rules:**
- server_startup_consistency.md
- rule_template (alwaysApply: true)
- documentation_usage
- api_standards

All changes are reflected in logs and documentation.

### Backup Compliance (May 2025)
All code, scripts, and documentation changes in BibleScholarProjectv2 have been mirrored to BibleScholarProjectClean as of this sync, in compliance with always-on Cursor rules and the single-source-of-truth and backup requirements. See logs/backup_sync.log for details.

**Enforced rules:**
- rule_template (alwaysApply: true)
- single-source-of-truth.mdc
- documentation_usage
- server_startup_consistency.md
- Backup/clean sync as described in the README and docs 

### Web App Enhancements
- **Contextual Insights API**: Now returns `model_config` in `/api/contextual_insights/insights` and logs configurations to `logs/contextual_insights.log` and program-specific logs to `logs/contextual_insights_program.log`.
- **Vector Search Demo**: Supports `/api/vector-search` endpoint for pgvector-based semantic search; results can be saved to `logs/vector_search_results.json` for validation. 

- **Testing**: Comprehensive unit and integration tests in `tests/`, excluding legacy folders via `pytest.ini`.
- **Backup**: Mirrored to `BibleScholarProjectClean` for safety.
- **Update Process**: The `BibleScholarProjectClean` folder is the always-updated, validated canonical copy. After validating changes in `BibleScholarProjectv2`, update the clean folder to match the current, working state. Do not treat this as a generic backup or mirror; only update with validated, standards-compliant files. 
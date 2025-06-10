# Fixing psycopg2/psycopg3 Compatibility Issues

## Overview

This document outlines the changes needed to ensure proper compatibility between psycopg3 and LangChain with PGVector in the BibleScholarLangChain project. The issue stems from mixed usage of `psycopg` (psycopg3) and `psycopg2.extras` imports in key files.

## Key Files Modified

1. `BibleScholarProjectv2/src/api/vector_search_api.py`:
   - Removed: `from psycopg2.extras import RealDictCursor`
   - Now uses: `import psycopg` with `conn.row_factory = psycopg.rows.dict_row`

2. `BibleScholarProjectv2/src/database/secure_connection.py`:
   - Removed: `from psycopg2.extras import RealDictCursor`
   - Now uses: `import psycopg` with `conn.row_factory = psycopg.rows.dict_row`

## New Scripts Created

1. `BibleScholarLangChain/scripts/step3_check.py`:
   - Checks for psycopg3 installation
   - Uninstalls psycopg2 if present
   - Checks for existing vector store in bible.verse_embeddings

2. `BibleScholarLangChain/scripts/verify_psycopg3.py`:
   - Comprehensive verification of psycopg3 and langchain-postgres compatibility
   - Checks if PGVector is using psycopg3 properly

## Changes to Setup Process

1. **Step 1** in `setup.ipynb`:
   - Added code to uninstall psycopg2 before installing dependencies
   - Verifies psycopg3 is properly installed and psycopg2 is not importable

2. **Step 3** in `setup.ipynb`:
   - Runs step3_check.py to verify environment and database setup
   - Checks for existing bible.verse_embeddings table
   - Modified load_bible_data.py to use existing store if available

3. **Step 4** in `setup.ipynb`:
   - Updated contextual_insights_api.py to use psycopg3 consistently
   - Added code to check for and use existing verse_embeddings when available

## MCP Rules Update

Updated `mcp_rules.md` to include the new scripts in the required file structure:
```
Required: `config.json`, `.env`, `scripts\db_config.py`, `scripts\step3_check.py`, `scripts\verify_psycopg3.py`, ...
```

## Testing

The setup notebook now includes steps to:
1. Verify psycopg3 is installed (version 3.1.8)
2. Confirm psycopg2 is not importable
3. Check for existing vector store
4. Test database connections with psycopg3
5. Verify API health with proper psycopg3 usage

## Implementation Instructions

1. Replace the content of Step 1, Step 3, and Step 4 cells in `setup.ipynb` with the updated code from `setup_notebook_updates.py`
2. Create the new scripts in the appropriate locations
3. Run the notebook cells sequentially to verify each step works properly

These changes ensure compatibility between the BibleScholarLangChain project, LangChain, and PGVector, allowing proper PostgreSQL connectivity with psycopg3. 
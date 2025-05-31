# Book Name Normalization for DB Queries

All code that queries the database by book name must use the `parse_reference` utility and/or `normalize_book_name` to ensure the correct abbreviation is used. This prevents silent data loss and ensures robust, cross-version compatibility.

## Requirements
- Use `parse_reference(reference)` to extract (book_abbr, chapter, verse) for all queries.
- Never use raw user input or canonical names directly in DB queries.
- Add tests for edge cases (e.g., 'John', 'john', 'Jn', 'Jhn', etc.) to ensure normalization is robust.
- Reviewers must reject code that does not use these utilities for DB queries.

---
type: always
description: This rule must always be included for all DB queries involving book names.
globs:
  - "src/**/*.py"
  - "scripts/*.py"
  - "tests/**/*.py"
alwaysApply: true 
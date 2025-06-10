# ETL Rules

## Purpose
Ensure all ETL (Extract, Transform, Load) processes are reliable, reproducible, and maintainable.

---

## Requirements
- Use environment variables for all file paths and database connections.
- Log all ETL steps and errors.
- Validate input data before processing.
- Use batch operations for large data loads.
- Handle missing or malformed data gracefully.
- Write modular, testable ETL scripts.

---

## Example
```python
import os
from dotenv import load_dotenv
load_dotenv()

input_file = os.getenv('INPUT_FILE')
if not input_file:
    raise ValueError('INPUT_FILE not set')
# ...
```

---

## Maintenance
- Update this rule if ETL conventions or data requirements change.
- Reference: [Cursor ETL Rules](https://docs.cursor.so/rules/etl) 
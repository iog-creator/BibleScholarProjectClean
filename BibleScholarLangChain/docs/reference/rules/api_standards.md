# API Standards

## Purpose
Ensure all API endpoints are consistent, well-documented, and follow best practices for error handling, security, and maintainability.

---

## Requirements
- Use Flask blueprints for modularity.
- All endpoints must return JSON responses with appropriate status codes.
- Log all errors and important events.
- Validate all input data and handle errors gracefully.
- Use environment variables for configuration (never hardcode secrets).
- Prefix all API routes with `/api/`.

---

## Example
```python
@app.route('/api/example', methods=['POST'])
def example():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input'}), 400
    # ...
    return jsonify({'result': 'ok'})
```

---

## Maintenance
- Update this rule if API conventions or security requirements change.
- Reference: [Cursor API Standards](https://docs.cursor.so/rules/api) 
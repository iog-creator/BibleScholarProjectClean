## Compliance
- Follows `.cursor/rules/rule_creation_guide.mdc` for structure.
- Follows `.cursor/rules/logging_and_error_handling.mdc` for logging standards.
- Enforced by always-on and standards rules.

## Pruning & Retention
- Rules older than 30 days are automatically pruned daily with backups.
- Backup content is appended under a `# Backup (ignore unless restore needed)` marker.

## See Also 
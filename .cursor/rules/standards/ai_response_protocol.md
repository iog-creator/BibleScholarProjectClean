---
description: Enforces a strict AI/agent response protocol for BibleScholarProjectv2, requiring rule loading, validation, and explicit compliance with the Cursor Rules Guide at the start and end of every response.
globs:
  - "*"
type: always
alwaysApply: true
---

# AI/Agent Response Protocol Rule

## Purpose
To ensure every AI/agent response is robust, standards-compliant, and always aligned with project rules and the Cursor Rules Guide.

## Protocol

**Before responding to any user query:**
- Load all always-on rules from `.cursor/rules/` (especially standards and enforcement rules).
- Check the README for referenced rules and project standards.
- Reference the [Cursor Rules Guide](https://docs.cursor.com/context/rules) for rule structure and update process.
- Prioritize the `server_startup_consistency.md` rule and any "alwaysApply: true" rules.

**After generating a response:**
- Validate that all advice, code, and documentation changes comply with loaded rules.
- State which rules were enforced or if a rule update is needed.
- Remind to keep rules, code, and docs in sync.

## Enforcement
- Any deviation from this protocol is a critical error and must be fixed before proceeding.
- If a rule or process is missing, recommend creating or updating a rule.

## Rule Update Process
- Edit this rule in `.cursor/rules/standards/ai_response_protocol.md`.
- Update related documentation and README as needed.
- Reference the [Cursor Rules Guide](https://docs.cursor.com/context/rules) for best practices.

**This rule is mandatory and must be followed for all AI/agent work in this project.** 
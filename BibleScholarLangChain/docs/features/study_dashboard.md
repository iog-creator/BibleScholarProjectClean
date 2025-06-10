---
title: Study Dashboard UI
last_updated: 2024-06-10
description: BibleScholarProject Study Dashboard UI, features, test cases, and integration
related_docs:
  - ../reference/API_REFERENCE.md
  - ../../README.md
  - ../../.cursor/rules/ui_testing_standards.md
---

# Study Dashboard UI

## Overview
A responsive, widescreen-optimized dashboard for Bible study, featuring:
- Three-column layout (Options, Verse+Chat, Historical Context)
- Double-click expansion/swapping
- Linked scrolling and split-color circle for timelines
- Linked events list
- Verse search and AI Study Companion chat
- Theme and tone toggles
- Widescreen and mobile optimization

## Layout
- **Left:** Options (translation, tone, theme)
- **Center:** Verse card, AI Study Companion
- **Right:** Historical Context (timelines, details, linked events)

## Features
- **Translation Options**: Select from KJV, ASV, TAHOT, or YLT to view verses in different translations. TAHOT provides tagged Hebrew Old Testament data.
- **Double-click Expansion:** Expand any panel to center, swap others
- **Linked Scrolling:** Timelines scroll in sync, split-color circle links events
- **Linked Events List:** Shows all linked event pairs when expanded
- **Verse Search:** Search bar fetches verses via `/api/search?q=<query>&type=verse` and displays the returned list of verses.
- **AI Study Companion:** Uses `/api/contextual_insights/insights` to provide insights for verses and general questions, with detailed insights available via a modal.
- **Theme/Tone Toggles:** Switch between light/dark and simple/detailed
- **Responsive Layout:** Optimized for 1440px, 1920px+, and mobile
- **Image Error Handling:** Images in the History Details column have error handling; if an image fails to load, a fallback "Image unavailable" placeholder is displayed.

## Test Cases
- See `tests/test_study_dashboard_ui.py` for automated UI/API tests
- Manual: verify all features above, including error handling and edge cases
- `/api/search` verse endpoint is validated in `test_verse_search_api`.

## API Usage
- `/api/search?q=...&type=verse` — Verse search
- `/api/contextual_insights/insights` — AI Study Companion (handles both verse and general queries)
  - **Parameters:**
    - `type`: 'verse' or 'text_snippet'
    - `reference`: (for type 'verse')
    - `text`: (for type 'text_snippet')
    - `translation`: translation code (KJV, ASV, TAHOT, YLT)

## Maintenance Notes
- Update tests and docs with any UI/API changes
- Reference and update Cursor rules for UI and testing standards
- Integrate with MCP server for automated test runs and health checks

## Developer Experience and Testing Notes
- Servers are started in debug mode and remain running for development; they are not auto-terminated after tests.
- The UI test runner and all tests print clear, colorized, human-readable status and error messages for each step.
- AI inference (LM Studio) is explicitly checked before tests run; actual AI responses are printed in the test output for verification.
- If a required service (API server, LM Studio) is not running, the test runner prints a clear error and fails fast.
- Logs are available in `logs/api_server.log`. To stop the server, use Ctrl+C in the server window or terminate the process.
- All practices follow the Logging and Error Handling, UI Testing Standards, and Documentation System rules.

## Screenshots
- _[Add screenshots of each panel, expanded view, and mobile layout]_ 

## Troubleshooting
- **AI Chat Fails to Respond**: Check that the LM Studio server is running at `http://localhost:1234/v1` and is reachable. Verify network connectivity and that the correct model is loaded in LM Studio. If using a mock backend, only mock responses will be returned. 
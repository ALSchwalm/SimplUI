# Specification: Python 3.11 Support

## Overview
The project currently fails to run on Python 3.11 due to syntax errors (specifically around `except` blocks) and lacks official configuration for this version. This track aims to make Python 3.11 a fully supported minimum version, ensuring the codebase is compatible and the project metadata reflects this support.

## Functional Requirements
1.  **Code Compatibility:** The codebase must run without syntax errors on Python 3.11. Specifically, `except` blocks using syntax invalid in 3.11 (e.g., multiple exception types without parentheses) must be corrected.
2.  **Configuration Update:** The project configuration (e.g., `pyproject.toml`, `requires-python`) must explicitly allow Python 3.11.
3.  **Verification:** The application and its test suite must pass successfully in a Python 3.11 environment.

## Non-Functional Requirements
*   **Backward Compatibility:** Changes should ideally remain compatible with previously supported versions (e.g., 3.10) if possible, though 3.11 is the new target minimum.
*   **No Regression:** The fix must be permanent and protected by configuration to prevent future regressions.

## Acceptance Criteria
*   `python --version` confirms 3.11 environment.
*   The application starts and runs without `SyntaxError`.
*   All automated tests pass in the 3.11 environment.
*   Project metadata officially lists Python 3.11 support.

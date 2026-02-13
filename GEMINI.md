# GEMINI.md - Project Context (Multi-Platform Edition)

## Project Overview
**All_To_PDF** is a highly adaptive PDF conversion suite. It is designed to provide a seamless "one-click" conversion experience for Web URLs, images, and Microsoft Office documents, regardless of the hosting environment.

### Core Architecture
- **Web Layer**: FastAPI provides an asynchronous API to handle high-concurrency PDF requests.
- **Conversion Engine**:
    - **Web**: Playwright (Chromium) with an `auto_scroll` injection logic.
    - **Windows Native**: `pywin32` (COM Interop) for native MS Office rendering.
    - **Linux/Docker**: `LibreOffice` (Headless mode) for server-side document processing.
- **Frontend**: A modern Bootstrap 5 UI with async fetch and blob download handling.

---

## Technical Details

### Async Orchestration
The project uses `nest_asyncio` to allow Playwright's event loop to run inside FastAPI's event loop, solving common `RuntimeError` issues in asynchronous environments.

### Deployment Strategies

#### Native Windows
Optimized for local productivity. It attempts to use the user's installed Microsoft Office suite for maximum formatting accuracy.

#### Docker (Debian-based)
Optimized for portability. The `Dockerfile` handles:
1. Installation of `libreoffice` (full suite).
2. Installation of all necessary Linux libraries (`libnss3`, `libgbm1`, etc.) for Playwright.
3. Creation of temporary volumes for `uploads/` and `outputs/`.

### File Lifecycle Management
To ensure security and low disk usage, the app implements a `BackgroundTasks` cleanup mechanism:
- Files are assigned a `UUID` to prevent path traversal and naming conflicts.
- A delayed cleanup task runs 60 seconds after the response is served, deleting both input and output artifacts.

---

## Quick Reference
- **Entry Point**: `app.py`
- **Port**: 8000
- **Main Dependencies**: `fastapi`, `playwright`, `pywin32` (Windows), `LibreOffice` (Linux/Docker).
 

 
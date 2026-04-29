# Technical Implementation Plan: Photo Organizer

## 1. Tech Stack
- **Frontend:** Vite (Vanilla JS template), CSS3 (Grid/Flexbox), and Native Web APIs.
- **Backend:** FastAPI (Python 3.12).
- **Database:** SQLite (Local file: photo_metadata.db).
- **Image Processing:** Pillow (PIL) for EXIF metadata extraction.

## 2. Architecture & Data Flow
- **Local-Only Principle:** The frontend never "uploads" files. It sends a local directory path to the backend. The backend scans that path directly on your disk.
- **State Management:** The "Source of Truth" is the SQLite database. The frontend fetches the full list of indexed photos on load and filters/groups them in-memory.
- **Static Serving:** `app.py` uses `StaticFiles` to serve the built Vite assets from the `static/dist` folder.

## 3. Core Components
- **`file_processor.py`**: A utility module to handle EXIF extraction and SQLite INSERT/UPDATE operations.
- **`app.py`**: The API layer.
    - `POST /scan`: Receives a folder path and triggers the `file_processor`.
    - `GET /photos`: Returns a JSON array of all indexed photo metadata.
- **`main.js`**: The frontend controller.
    - Fetches photos.
    - Groups them by `date_taken`.
    - Renders the HTML structure for "Date Albums."

## 4. UI/UX Plan
- **Tile Interface:** A responsive grid using `grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))`.
- **Drag-and-Drop:** Use the Native HTML5 Drag and Drop API to allow users to move tiles between album sections.

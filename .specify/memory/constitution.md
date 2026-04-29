Photo Organizer Constitution
Core Principles
I. Vanilla-First & Minimalist
The application must prioritize vanilla HTML, CSS, and JavaScript. Libraries (like Vite or Pillow) are only introduced when browser APIs or standard libraries are insufficient. No heavy UI frameworks (React/Angular) unless explicitly ratified.

II. Local-Only Persistence
User data, images, and metadata must remain local. No cloud uploads. Metadata is stored in a local SQLite database (photo_metadata.db). Absolute file paths are used to reference local assets.

III. Spec-First Development (NON-NEGOTIABLE)
No code is written without a corresponding .spec artifact. The workflow must strictly follow: /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement.

IV. Protocol-Based Communication
The backend (FastAPI) and frontend (Vite) must communicate via clear JSON contracts. The backend is a "dumb" data provider; the frontend is responsible for the interactive UI logic (Drag-and-Drop).

Technical Constraints
Backend: Python 3.12+, FastAPI, SQLite.

Frontend: Vite, Vanilla JS, CSS Grid for "Tile" views.

Metadata: EXIF extraction via Pillow; Fallback to filesystem mtime if EXIF is missing.
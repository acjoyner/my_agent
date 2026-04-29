# Photo Organizer Constitution

## Core Principles

I. Vanilla-First & Minimalist
The application must prioritize vanilla HTML, CSS, and JavaScript. Libraries (like Vite or Pillow) are only introduced when browser APIs or standard libraries are insufficient. No heavy UI frameworks (React/Angular) unless explicitly ratified.

II. Local-Only Persistence
User data, images, and metadata must remain local. No cloud uploads. Metadata is stored in a local SQLite database (photo_metadata.db). Absolute file paths are used to reference local assets.

III. Spec-First Development (NON-NEGOTIABLE)
No code is written without a corresponding .spec artifact. The workflow must strictly follow:
/speckit.specify -> /speckit.plan -> /speckit.tasks -> /speckit.implement.

IV. Protocol-Based Communication
The backend (FastAPI) and frontend (Vite) must communicate via clear JSON contracts. The backend is the single source of truth for filesystem operations.

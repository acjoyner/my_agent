#!/bin/bash
# Start the Personal Assistant Agent web UI
# Usage: ./run.sh
# Then open: http://localhost:8000

cd "$(dirname "$0")"
python -m uvicorn app:app --reload --port 8000

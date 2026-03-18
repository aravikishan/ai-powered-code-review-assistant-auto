#!/bin/bash
set -e
echo "Starting AI-Powered Code Review Assistant..."
uvicorn app:app --host 0.0.0.0 --port 9126 --workers 1

#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

export FLASK_APP=s_api_request.py
export FLASK_ENV=production

# Render uses the PORT environment variable.
echo "Starting Flask on port ${PORT:-5000}..."
flask run --host=0.0.0.0 --port=${PORT:-5000}
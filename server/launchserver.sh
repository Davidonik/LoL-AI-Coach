#!/usr/bin/env bash
# Exit immediately if a command fails
set -e

# Change to the directory containing this script
cd "$(dirname "$0")"

# Set environment variables
export FLASK_APP=s_api_request.py
export FLASK_ENV=development

# Start the Flask server
flask run --host=0.0.0.0 --port=10000
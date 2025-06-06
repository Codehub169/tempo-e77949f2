#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Navigate to the directory where the script is located (optional, but good practice)
# cd "$(dirname "$0")"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies for Tailwind CSS
# Check if package.json exists before trying to install npm packages
if [ -f package.json ]; then
  echo "Installing Node.js dependencies..."
  npm install
else
  echo "package.json not found, skipping npm install."
fi

# Build Tailwind CSS
# Check if Tailwind CSS needs to be built
if [ -f package.json ] && [ -d node_modules ] && [ -f src/input.css ] && [ -f tailwind.config.js ]; then
  echo "Building Tailwind CSS..."
  npx tailwindcss -i ./src/input.css -o ./static/css/style.css --minify
else
  echo "Skipping Tailwind CSS build due to missing files (package.json, node_modules, src/input.css, or tailwind.config.js)."
  # Create an empty style.css if it's missing, so Flask doesn't complain
  mkdir -p ./static/css
  touch ./static/css/style.css
fi

# Initialize database if it doesn't exist (assuming app.py handles this or you have a separate script)
# echo "Initializing database (if needed)..."
# python -c "from app import init_db; init_db()" # Example, adjust as per your app.py

# Start the Flask application using Gunicorn
echo "Starting Flask application on port 9000..."
gunicorn --bind 0.0.0.0:9000 app:app

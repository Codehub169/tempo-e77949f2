#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the Flask app entry point
FLASK_APP_DEFAULT="app.py"
FLASK_APP_MODULE=${FLASK_APP_MODULE:-$FLASK_APP_DEFAULT}

# Define the host and port
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-9000}

# Define the number of Gunicorn workers (adjust based on your server's resources)
# General recommendation: 2-4 x (number of CPU cores) + 1
# For simplicity, we'll default to 3 if not set.
WORKERS=${GUNICORN_WORKERS:-3}

# Define the Gunicorn worker class (sync is default, but gevent or eventlet can be used for async apps)
WORKER_CLASS=${GUNICORN_WORKER_CLASS:-sync}

# Define Gunicorn access log format
ACCESS_LOG_FORMAT='%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Function to run Tailwind CSS build
build_css() {
    echo "Building Tailwind CSS..."
    if [ -f "./package.json" ] && [ -f "./tailwind.config.js" ] && [ -d "./src" ] && [ -f "./src/input.css" ]; then
        if ! command -v npm &> /dev/null && ! command -v npx &> /dev/null; then
            echo "Error: npm/npx is not installed. Cannot build Tailwind CSS."
            echo "Please install Node.js and npm."
            exit 1
        fi
        # Ensure node_modules are installed
        if [ -f "package-lock.json" ] && [ ! -d "node_modules" ]; then
            echo "package-lock.json found but node_modules missing. Running npm ci..."
            npm ci # Use ci for cleaner installs from lock file
        elif [ ! -d "node_modules" ]; then
             echo "node_modules directory missing. Running npm install..."
             npm install # Creates node_modules and package-lock.json if not present
        fi # If node_modules exists, assume it's correct for speed.
        
        # Check if tailwindcss command is available via npx
        if ! npx tailwindcss --help &> /dev/null; then 
            echo "Tailwind CSS not found or not executable via npx. Ensure it's in devDependencies and npm install/ci was successful."
            # Exit if in production, as CSS build is critical.
            # In development, the user might have a watch process or handle it manually.
            if [ "${FLASK_ENV}" != "development" ]; then
                exit 1
            fi 
        fi

        echo "Running Tailwind CSS build command..."
        mkdir -p ./static/css # Ensure the target directory exists
        npx tailwindcss -i ./src/input.css -o ./static/css/style.css --minify
        echo "Tailwind CSS build complete."
    else
        echo "Skipping Tailwind CSS build: Essential files (package.json, tailwind.config.js, src/input.css) or src/ directory not found."
        # Create an empty style.css if it's missing, so Flask doesn't complain if build is skipped and templates link to it.
        mkdir -p ./static/css
        touch ./static/css/style.css
        echo "Created empty ./static/css/style.css as a fallback."
    fi
}

# Check if running in development or production
# The FLASK_ENV environment variable is commonly used for this.

if [ "${FLASK_ENV}" = "development" ]; then
    echo "Starting in DEVELOPMENT mode..."
    # Ensure Flask and other Python dependencies are installed for development
    if [ -f "requirements.txt" ]; then
        echo "Installing/checking Python dependencies for development..."
        pip install -r requirements.txt
    fi
    # In development, Tailwind might be watched separately or built on demand.
    # We run a build here for initial setup or if no watch process is active.
    build_css 
    echo "Starting Flask development server..."
    # Run the Flask app directly using the Flask development server
    # app.py should handle host/port for development mode (e.g. in if __name__ == '__main__')
    python "${FLASK_APP_MODULE}"
else
    echo "Starting in PRODUCTION mode..."
    # In production, CSS must be built before starting Gunicorn.
    build_css

    # Ensure Gunicorn is installed (it should be in requirements.txt for production environments)
    if ! command -v gunicorn &> /dev/null; then
        echo "Gunicorn not found. Please ensure it is listed in requirements.txt and installed."
        # Optionally, attempt to install it if running in a less controlled environment
        # echo "Attempting to install Gunicorn..."
        # pip install gunicorn
        # If Gunicorn is critical and not found, exiting is safer for production.
        exit 1
    fi
    echo "Starting Gunicorn production server..."
    # Start Gunicorn server
    # The format app:app means Gunicorn will look for an object named 'app' in a Python module named 'app.py'.
    exec gunicorn --bind "${HOST}:${PORT}" \
                  --workers "${WORKERS}" \
                  --worker-class "${WORKER_CLASS}" \
                  --access-logfile '-' \
                  --error-logfile '-' \
                  --access-logformat "${ACCESS_LOG_FORMAT}" \
                  "${FLASK_APP_MODULE%.py}:app"
fi

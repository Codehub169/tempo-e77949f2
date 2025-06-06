# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install Node.js and npm for Tailwind CSS build
# Using NodeSource repository for a specific Node.js version (e.g., LTS - Long Term Support)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg ca-certificates && \
    # The NodeSource setup script will handle adding the GPG key and repository
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    # Clean up APT caches and lists to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Verify Node.js and npm installation (optional, good for debugging)
RUN node --version
RUN npm --version

# Copy application dependency files first to leverage Docker cache
COPY requirements.txt ./
COPY package.json ./
# Copy package-lock.json if it exists; an asterisk handles potential variations like package-lock.jsonc
COPY package-lock.json* ./

# Install Python dependencies
# Using --no-cache-dir to reduce image size
# Python packages are installed globally; virtual environments are not typically used in simple container setups like this
# but could be an option for more complex scenarios.
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies (including devDependencies like tailwindcss for the build step)
# Use npm ci if package-lock.json exists for deterministic and faster builds, else npm install.
RUN if [ -f package-lock.json ]; then \
        echo "package-lock.json found, running npm ci"; \
        npm ci; \
    else \
        echo "package-lock.json not found or is package-lock.jsonc, running npm install"; \
        npm install; \
    fi

# Copy the rest of the application code into the container
# This includes your Flask app, templates, static files, src for CSS, etc.
# Ensure a .dockerignore file is used locally to prevent copying unnecessary files (e.g., .git, local venv, node_modules)
COPY . . 

# Build Tailwind CSS (ensure src/input.css and tailwind.config.js are present from COPY . .)
# The npx command will use the tailwindcss installed from devDependencies.
RUN echo "Attempting to build Tailwind CSS in Docker..." && \
    if [ ! -f "./src/input.css" ]; then echo "Error: src/input.css not found!"; exit 1; fi && \
    if [ ! -f "./tailwind.config.js" ]; then echo "Error: tailwind.config.js not found!"; exit 1; fi && \
    mkdir -p ./static/css && \
    npx tailwindcss -i ./src/input.css -o ./static/css/style.css --minify && \
    echo "Tailwind CSS build successful."

# Make port 9000 available to the world outside this container
EXPOSE 9000

# Define environment variables (can be overridden at runtime)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production # Default to production; set to 'development' for dev server via docker run -e
ENV GUNICORN_WORKERS=3
ENV PYTHONUNBUFFERED=1 # Ensures print statements and logs are sent straight to stdout/stderr, crucial for Docker logging

# Unset proxy environment variables to prevent interference from the build host leaking into the container runtime
ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""
ENV http_proxy=""
ENV https_proxy=""
ENV NO_PROXY="localhost,127.0.0.1"

# Create a non-root user and group for security
ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --no-log-init -m -r -g ${APP_USER} ${APP_USER}
# -m creates home directory for the user (e.g. /home/appuser)
# -r creates a system user

# Ensure the startup script is executable
RUN chmod +x ./startup.sh

# Change ownership of the app directory to the new user
# This allows the application (running as appuser) to write files if needed (e.g., SQLite DB, logs in /app)
RUN chown -R ${APP_USER}:${APP_USER} /app

# Switch to the non-root user
USER ${APP_USER}

# Command to run the application using the startup script
# The startup.sh script will handle environment-specific logic (dev vs prod)
CMD ["./startup.sh"]
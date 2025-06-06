# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install Node.js and npm for Tailwind CSS build
# Using NodeSource repository for a specific Node.js version (e.g., LTS - Long Term Support)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
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
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies (including devDependencies like tailwindcss for the build step)
# Use npm ci if package-lock.json exists for deterministic and faster builds, else npm install.
RUN if [ -f package-lock.json ]; then \
        echo "package-lock.json found, running npm ci"; \
        npm ci; \
    else \
        echo "package-lock.json not found, running npm install"; \
        npm install; \
    fi

# Copy the rest of the application code into the container
# This includes your Flask app, templates, static files, src for CSS, etc.
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

# Define environment variables (can be overridden at runtime, e.g., `docker run -e FLASK_ENV=development ...`)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production # Default to production; set to 'development' for dev server via docker run -e
ENV GUNICORN_WORKERS=3
ENV PYTHONUNBUFFERED=1 # Ensures print statements and logs are sent straight to stdout/stderr, crucial for Docker logging

# Ensure the startup script is executable
RUN chmod +x ./startup.sh

# Command to run the application using the startup script
# The startup.sh script will handle environment-specific logic (dev vs prod)
CMD ["./startup.sh"]

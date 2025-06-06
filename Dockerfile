# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Node.js and npm for Tailwind CSS compilation
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python dependency files and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Node.js dependency files and install dependencies
COPY package.json package-lock.json* ./
# Adding a check for package-lock.json as it might not always exist initially
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy Tailwind CSS configuration and source CSS file
COPY tailwind.config.js .
COPY src/input.css ./src/input.css

# Create static directories and build Tailwind CSS
RUN mkdir -p static/css
RUN npx tailwindcss -i ./src/input.css -o ./static/css/style.css --minify

# Copy the rest of the application code into the container
COPY . .

# Create a dummy database file if it's not present, to avoid startup issues if app expects it
# This is a placeholder. Actual database initialization should be handled by the application or a migration script.
RUN if [ ! -f database/portfolio.db ]; then mkdir -p database && touch database/portfolio.db; fi

# Expose the port the app runs on
EXPOSE 9000

# Define environment variables (if any, e.g., FLASK_ENV)
ENV FLASK_ENV=production

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "app:app"]

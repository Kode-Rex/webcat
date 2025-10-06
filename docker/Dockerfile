FROM python:3.13-slim

WORKDIR /app

# Copy project metadata and structure
COPY pyproject.toml README.md LICENSE /app/

# Copy docker module (source code and all subdirectories)
COPY docker/ /app/docker/

# Copy examples
COPY examples/ /app/examples/

# Install package with dependencies from pyproject.toml
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /app

# Create log directory with proper permissions
RUN mkdir -p /var/log/webcat && chmod 755 /var/log/webcat

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV LOG_LEVEL=INFO
ENV LOG_DIR=/var/log/webcat
ENV WEBCAT_MODE=demo

# Expose the port
EXPOSE 8000

# Set working directory to docker module for runtime
WORKDIR /app/docker

# Command to run the application
CMD ["python", "cli.py", "--mode", "demo", "--host", "0.0.0.0"]

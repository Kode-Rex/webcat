FROM python:3.11-slim

WORKDIR /app

# Copy necessary files
COPY docker/requirements.txt /app/
COPY docker/mcp_server.py /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create log directory with proper permissions
RUN mkdir -p /var/log/webcat && chmod 755 /var/log/webcat

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV LOG_LEVEL=INFO
ENV LOG_DIR=/var/log/webcat

# Expose the configurable port
EXPOSE ${PORT}

# Command to run the application
CMD python mcp_server.py 
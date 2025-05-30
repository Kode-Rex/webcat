FROM python:3.11-slim

WORKDIR /app

# Copy necessary files
COPY docker/requirements.txt /app/
COPY docker/mcp_server.py /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose the configurable port
EXPOSE ${PORT}

# Command to run the application with uvicorn using the configurable port
CMD uvicorn mcp_server:app --host 0.0.0.0 --port ${PORT} 
FROM python:3.11-slim

WORKDIR /app

# Copy necessary files
COPY docker/requirements.txt /app/
COPY docker/*.py /app/
COPY examples/ /app/examples/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create log directory with proper permissions
RUN mkdir -p /var/log/webcat && chmod 755 /var/log/webcat

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV LOG_LEVEL=INFO
ENV LOG_DIR=/var/log/webcat
ENV WEBCAT_MODE=demo

# Expose the configurable port and health port
EXPOSE ${PORT}
EXPOSE $((${PORT} + 1))

# Command to run the application
CMD python cli.py --mode ${WEBCAT_MODE:-demo} --host 0.0.0.0 --port ${PORT}

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set timezone to UTC (CRITICAL!)
ENV TZ=UTC
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src:/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cron \
        tzdata \
    && ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ /app/src/
COPY scripts/ /app/scripts/
COPY cron/ /app/cron/

# Copy key files (will be committed to Git)
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem

# Setup cron job
RUN chmod 0644 /app/cron/2fa-cron && \
    crontab /app/cron/2fa-cron

# Create volume mount points
RUN mkdir -p /data /cron && \
    chmod 755 /data /cron

# Expose API port
EXPOSE 8080

# Start cron and application
CMD cron && python3 -m uvicorn src.app:app --host 0.0.0.0 --port 8080

FROM python:3.9-slim

WORKDIR /app

# Set pip timeout and other environment variables
ENV PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and set up entrypoint script first
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Check for required environment variables\n\
required_vars=("EMAIL_USERNAME" "EMAIL_PASSWORD" "MONGODB_USERNAME" "MONGODB_PASSWORD")\n\
\n\
for var in "${required_vars[@]}"; do\n\
    if [ -z "${!var}" ]; then\n\
        echo "Error: Required environment variable $var is not set"\n\
        exit 1\n\
    fi\n\
done\n\
\n\
# Execute the main command\n\
exec "$@"' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Install dependencies in multiple steps for better caching and reliability
COPY requirements.txt .

# Install basic dependencies first
RUN pip install --no-cache-dir --timeout 100 pymongo>=4.0.0 pyyaml>=6.0.0 schedule>=1.1.0 python-dotenv>=0.19.0

# Install numpy and pandas separately (these are larger packages)
RUN pip install --no-cache-dir --timeout 100 numpy>=1.22.4 pandas>=1.5.0

# Copy application code last (changes most frequently)
COPY . .

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "app.py"]
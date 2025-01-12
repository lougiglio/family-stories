FROM python:3.9-slim

WORKDIR /app

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

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code last (changes most frequently)
COPY . .

# Add healthcheck
HEALTHCHECK --interval=5m --timeout=30s --retries=3 \
    CMD python -c "from app import FamilyStoriesApp; app = FamilyStoriesApp(); exit(0 if app.health_check() else 1)"

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "app.py"]
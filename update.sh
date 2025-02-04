#!/bin/bash

echo "Updating Family Stories application..."

# Pull latest changes
git pull

# Rebuild and restart containers
docker-compose -f build/docker-compose.yml down
docker-compose -f build/docker-compose.yml up -d --build

echo "Update complete! Showing logs..."
docker-compose -f build/docker-compose.yml logs -f
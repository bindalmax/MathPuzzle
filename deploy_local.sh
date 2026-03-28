#!/bin/bash

# --- Local Deployment Script for MathPuzzle ---

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting local deployment process...${NC}"

# 1. Ensure the data directory and highscores file exist for volume mounting
echo -e "Checking data persistence setup..."
if [ ! -d "data" ]; then
    mkdir data
    echo "Created 'data' directory."
fi

if [ ! -f "data/highscores.json" ]; then
    # If a root highscores exists, move it, otherwise create empty
    if [ -f "highscores.json" ]; then
        cp highscores.json data/highscores.json
        echo "Copied existing highscores.json to data directory."
    else
        echo "[]" > data/highscores.json
        echo "Created empty 'data/highscores.json'."
    fi
fi

# 2. Stop any existing containers to avoid port conflicts
echo -e "Stopping existing containers..."
docker-compose down

# 3. Build and Start the application
echo -e "${BLUE}Building and starting Docker containers...${NC}"
docker-compose up -d --build

# 4. Final check
if [ $? -eq 0 ]; then
    echo -e "${GREEN}SUCCESS: MathPuzzle is running locally!${NC}"
    echo -e "Access the web app at: ${BLUE}http://localhost:5001${NC}"
    echo -e "To view logs, run: ${BLUE}docker-compose logs -f web${NC}"
else
    echo "ERROR: Docker deployment failed. Check the logs for details."
    exit 1
fi

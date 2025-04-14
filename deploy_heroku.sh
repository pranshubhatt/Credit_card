#!/bin/bash

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "Heroku CLI is not installed. Please install it first."
    exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "Please login to Heroku first using: heroku login"
    exit 1
fi

# Create Heroku app if it doesn't exist
if ! heroku apps:info &> /dev/null; then
    echo "Creating Heroku app..."
    heroku create
fi

# Set environment variables
echo "Setting environment variables..."
heroku config:set PYTHON_VERSION=3.12.0
heroku config:set API_KEY=$(openssl rand -hex 32)
heroku config:set ENVIRONMENT=production
heroku config:set LOG_LEVEL=INFO

# Add PostgreSQL addon
echo "Adding PostgreSQL addon..."
heroku addons:create heroku-postgresql:hobby-dev

# Push to Heroku
echo "Deploying to Heroku..."
git push heroku main

echo "Deployment complete! Your app should be running at:"
heroku open 
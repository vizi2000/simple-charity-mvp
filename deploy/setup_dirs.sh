#!/bin/bash

# Setup directories and initial data files for deployment

DEPLOY_PATH="/var/www/simplepaymentgate"

echo "Setting up directory structure..."

# Create all necessary directories
mkdir -p $DEPLOY_PATH/backend/app/data
mkdir -p $DEPLOY_PATH/backend/static/uploads/logos
mkdir -p $DEPLOY_PATH/frontend/dist
mkdir -p /var/log/simplepaymentgate

# Create initial empty payments.json if it doesn't exist
if [ ! -f "$DEPLOY_PATH/backend/app/data/payments.json" ]; then
    echo "[]" > $DEPLOY_PATH/backend/app/data/payments.json
fi

# Set proper permissions
chown -R www-data:www-data $DEPLOY_PATH
chmod -R 755 $DEPLOY_PATH
chmod -R 777 $DEPLOY_PATH/backend/app/data
chmod -R 777 $DEPLOY_PATH/backend/static/uploads

echo "Directory structure created successfully!"
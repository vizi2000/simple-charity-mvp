#!/bin/bash

# Quick deployment script for Simple Payment Gate
# This script assumes SSH key authentication is set up

set -e

echo "======================================"
echo "Quick Deploy to 192.168.100.159"
echo "======================================"

SERVER="root@192.168.100.159"
LOCAL_DIR="/Users/wojciechwiesner/ai/simple mvp charity"
REMOTE_DIR="/var/www/simplepaymentgate"

echo "1. Creating remote directories..."
ssh $SERVER "mkdir -p $REMOTE_DIR && mkdir -p /var/log/simplepaymentgate"

echo "2. Copying backend files..."
rsync -avz --exclude='venv*' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='test_*.py' --exclude='test_*.html' --exclude='*.log' \
  "$LOCAL_DIR/backend/" $SERVER:$REMOTE_DIR/backend/

echo "3. Copying frontend files..."
rsync -avz --exclude='node_modules' --exclude='dist' \
  "$LOCAL_DIR/frontend/" $SERVER:$REMOTE_DIR/frontend/

echo "4. Copying deployment configs..."
scp "$LOCAL_DIR/deploy/nginx.conf" $SERVER:/tmp/
scp "$LOCAL_DIR/deploy/backend.service" $SERVER:/tmp/
scp "$LOCAL_DIR/deploy/.env.production" $SERVER:$REMOTE_DIR/.env

echo "5. Installing on server..."
ssh $SERVER << 'EOF'
cd /var/www/simplepaymentgate

# Install system dependencies
apt-get update
apt-get install -y python3-venv python3-pip nginx nodejs npm

# Setup Python backend
cd backend
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Setup data directory
mkdir -p app/data
if [ ! -f app/data/payments.json ]; then
  echo "[]" > app/data/payments.json
fi

# Build frontend
cd ../frontend
npm install
npm run build

# Setup Nginx
cp /tmp/nginx.conf /etc/nginx/sites-available/simplepaymentgate
ln -sf /etc/nginx/sites-available/simplepaymentgate /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Setup systemd service
cp /tmp/backend.service /etc/systemd/system/simplepaymentgate-backend.service

# Set permissions
chown -R www-data:www-data /var/www/simplepaymentgate
chmod -R 755 /var/www/simplepaymentgate
chmod 777 /var/www/simplepaymentgate/backend/app/data

# Start services
systemctl daemon-reload
systemctl enable simplepaymentgate-backend
systemctl restart simplepaymentgate-backend
nginx -t && systemctl restart nginx

echo "Deployment complete!"
systemctl status simplepaymentgate-backend --no-pager
EOF

echo ""
echo "======================================"
echo "Deployment Successful!"
echo "======================================"
echo "Access at: http://192.168.100.159"
echo ""
echo "Check logs with:"
echo "  ssh $SERVER 'journalctl -u simplepaymentgate-backend -f'"
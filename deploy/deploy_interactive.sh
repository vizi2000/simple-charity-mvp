#!/bin/bash

# Interactive deployment script with password prompt

set -e

echo "============================================"
echo "Simple Payment Gate - Interactive Deployment"
echo "============================================"
echo ""
echo "Target Server: 192.168.100.159"
echo "Domain: simplepaymentgate"
echo ""

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo "No SSH key found. Would you like to:"
    echo "1) Generate SSH key and copy to server"
    echo "2) Continue with password authentication"
    read -p "Choice (1/2): " choice
    
    if [ "$choice" = "1" ]; then
        echo "Generating SSH key..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
        echo ""
        echo "Now copying SSH key to server (you'll need to enter password):"
        ssh-copy-id root@192.168.100.159
        echo "SSH key setup complete!"
    fi
fi

LOCAL_DIR="/Users/wojciechwiesner/ai/simple mvp charity"
SERVER="192.168.100.159"

echo ""
echo "Starting deployment..."
echo "You may be prompted for the server password."
echo ""

# Create deployment package
echo "Creating deployment package..."
cd "$LOCAL_DIR"
tar -czf /tmp/simplepaymentgate_deploy.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='venv*' \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='test_*.py' \
    --exclude='test_*.html' \
    backend frontend deploy

echo "Copying files to server..."
scp /tmp/simplepaymentgate_deploy.tar.gz root@$SERVER:/tmp/

echo "Executing deployment on server..."
ssh root@$SERVER 'bash -s' << 'DEPLOY_SCRIPT'
set -e

echo "Installing dependencies..."
apt-get update -qq
apt-get install -y python3-venv python3-pip nginx nodejs npm > /dev/null 2>&1

echo "Setting up application directory..."
mkdir -p /var/www/simplepaymentgate
cd /var/www/simplepaymentgate

echo "Extracting files..."
tar -xzf /tmp/simplepaymentgate_deploy.tar.gz

echo "Setting up Python backend..."
cd /var/www/simplepaymentgate/backend
python3 -m venv venv
./venv/bin/pip install --upgrade pip > /dev/null 2>&1
./venv/bin/pip install -r requirements.txt

echo "Creating data directories..."
mkdir -p app/data
mkdir -p static/uploads/logos
if [ ! -f app/data/payments.json ]; then
    echo "[]" > app/data/payments.json
fi

echo "Building frontend..."
cd /var/www/simplepaymentgate/frontend
npm install --silent
npm run build

echo "Configuring Nginx..."
cp /var/www/simplepaymentgate/deploy/nginx.conf /etc/nginx/sites-available/simplepaymentgate
ln -sf /etc/nginx/sites-available/simplepaymentgate /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "Setting up systemd service..."
cp /var/www/simplepaymentgate/deploy/backend.service /etc/systemd/system/simplepaymentgate-backend.service
cp /var/www/simplepaymentgate/deploy/.env.production /var/www/simplepaymentgate/.env

echo "Creating log directory..."
mkdir -p /var/log/simplepaymentgate

echo "Setting permissions..."
chown -R www-data:www-data /var/www/simplepaymentgate
chmod -R 755 /var/www/simplepaymentgate
chmod 777 /var/www/simplepaymentgate/backend/app/data
chmod -R 777 /var/www/simplepaymentgate/backend/static/uploads

echo "Starting services..."
systemctl daemon-reload
systemctl enable simplepaymentgate-backend > /dev/null 2>&1
systemctl restart simplepaymentgate-backend
nginx -t > /dev/null 2>&1 && systemctl restart nginx

echo ""
echo "Checking service status..."
systemctl is-active simplepaymentgate-backend > /dev/null 2>&1 && echo "✓ Backend is running" || echo "✗ Backend failed to start"
systemctl is-active nginx > /dev/null 2>&1 && echo "✓ Nginx is running" || echo "✗ Nginx failed to start"

echo ""
echo "Deployment completed successfully!"
DEPLOY_SCRIPT

# Cleanup
rm -f /tmp/simplepaymentgate_deploy.tar.gz

echo ""
echo "============================================"
echo "Deployment Complete!"
echo "============================================"
echo ""
echo "Your application is now available at:"
echo "  → http://$SERVER"
echo "  → http://simplepaymentgate (if DNS configured)"
echo ""
echo "Quick commands:"
echo "  Check backend logs:  ssh root@$SERVER 'journalctl -u simplepaymentgate-backend -f'"
echo "  Restart backend:     ssh root@$SERVER 'systemctl restart simplepaymentgate-backend'"
echo "  Check nginx logs:    ssh root@$SERVER 'tail -f /var/log/nginx/error.log'"
echo ""
echo "Next steps:"
echo "1. Test the application at http://$SERVER"
echo "2. Configure Fiserv webhook URL to: http://$SERVER/api/webhooks/fiserv"
echo "3. For production, set up SSL certificate (see DEPLOYMENT_GUIDE.md)"
echo ""
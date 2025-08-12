#!/bin/bash

# Create deployment package for manual transfer

echo "======================================"
echo "Creating Deployment Package"
echo "======================================"

LOCAL_DIR="/Users/wojciechwiesner/ai/simple mvp charity"
PACKAGE_NAME="simplepaymentgate_deploy_$(date +%Y%m%d_%H%M%S)"
PACKAGE_DIR="/tmp/$PACKAGE_NAME"

# Create package directory
mkdir -p "$PACKAGE_DIR"

echo "Copying backend files..."
cp -r "$LOCAL_DIR/backend" "$PACKAGE_DIR/"
# Clean up test files
find "$PACKAGE_DIR/backend" -name "test_*.py" -delete
find "$PACKAGE_DIR/backend" -name "test_*.html" -delete
find "$PACKAGE_DIR/backend" -name "*.pyc" -delete
find "$PACKAGE_DIR/backend" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf "$PACKAGE_DIR/backend/venv"*

echo "Copying frontend files..."
cp -r "$LOCAL_DIR/frontend" "$PACKAGE_DIR/"
rm -rf "$PACKAGE_DIR/frontend/node_modules"
rm -rf "$PACKAGE_DIR/frontend/dist"

echo "Copying deployment configs..."
cp -r "$LOCAL_DIR/deploy" "$PACKAGE_DIR/"

echo "Creating setup script..."
cat > "$PACKAGE_DIR/setup.sh" << 'EOF'
#!/bin/bash

# Server setup script
set -e

echo "======================================"
echo "Simple Payment Gate - Server Setup"
echo "======================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

DEPLOY_DIR="/var/www/simplepaymentgate"

echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-venv python3-pip nginx nodejs npm

echo "Creating application directory..."
mkdir -p "$DEPLOY_DIR"
cp -r backend "$DEPLOY_DIR/"
cp -r frontend "$DEPLOY_DIR/"

echo "Setting up Python environment..."
cd "$DEPLOY_DIR/backend"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "Creating data directories..."
mkdir -p app/data
mkdir -p static/uploads/logos
if [ ! -f app/data/payments.json ]; then
    echo "[]" > app/data/payments.json
fi

echo "Building frontend..."
cd "$DEPLOY_DIR/frontend"
npm install
npm run build

echo "Setting up Nginx..."
cp /root/deploy/nginx.conf /etc/nginx/sites-available/simplepaymentgate
ln -sf /etc/nginx/sites-available/simplepaymentgate /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "Setting up systemd service..."
cp /root/deploy/backend.service /etc/systemd/system/simplepaymentgate-backend.service
cp /root/deploy/.env.production "$DEPLOY_DIR/.env"

echo "Creating log directory..."
mkdir -p /var/log/simplepaymentgate

echo "Setting permissions..."
chown -R www-data:www-data "$DEPLOY_DIR"
chmod -R 755 "$DEPLOY_DIR"
chmod 777 "$DEPLOY_DIR/backend/app/data"
chmod -R 777 "$DEPLOY_DIR/backend/static/uploads"

echo "Starting services..."
systemctl daemon-reload
systemctl enable simplepaymentgate-backend
systemctl restart simplepaymentgate-backend
nginx -t && systemctl restart nginx

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo "Application available at: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Check service status:"
echo "  systemctl status simplepaymentgate-backend"
echo "  systemctl status nginx"
echo ""
echo "View logs:"
echo "  journalctl -u simplepaymentgate-backend -f"
EOF

chmod +x "$PACKAGE_DIR/setup.sh"

# Create archive
cd /tmp
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

echo ""
echo "======================================"
echo "Package Created Successfully!"
echo "======================================"
echo ""
echo "Package location: /tmp/$PACKAGE_NAME.tar.gz"
echo ""
echo "Manual deployment steps:"
echo ""
echo "1. Copy package to server:"
echo "   scp /tmp/$PACKAGE_NAME.tar.gz root@192.168.100.159:/root/"
echo ""
echo "2. SSH to server:"
echo "   ssh root@192.168.100.159"
echo ""
echo "3. Extract and run setup:"
echo "   cd /root"
echo "   tar -xzf $PACKAGE_NAME.tar.gz"
echo "   cd $PACKAGE_NAME"
echo "   ./setup.sh"
echo ""
echo "The setup script will handle everything automatically!"
echo ""

# Show package size
SIZE=$(du -h "/tmp/$PACKAGE_NAME.tar.gz" | cut -f1)
echo "Package size: $SIZE"
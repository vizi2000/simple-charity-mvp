#!/bin/bash

# Production deployment script for charity payment platform
# Server: borgtools.ddns.net
# User: vizi

set -e

echo "🚀 Starting production deployment..."

# Configuration
SERVER="borgtools.ddns.net"
USER="vizi"
REMOTE_DIR="/var/www/html/bramkamvp"
BACKEND_PORT=8000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📦 Creating deployment package...${NC}"

# Create temporary deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "Using temp directory: $DEPLOY_DIR"

# Copy backend files
echo -e "${YELLOW}Copying backend files...${NC}"
cp -r backend "$DEPLOY_DIR/"

# Copy frontend build
echo -e "${YELLOW}Copying frontend build...${NC}"
cp -r frontend/dist "$DEPLOY_DIR/frontend_dist"

# Create requirements file for production
cat > "$DEPLOY_DIR/requirements.txt" <<EOF
fastapi==0.116.1
uvicorn==0.35.0
python-multipart==0.0.20
httpx==0.28.1
qrcode==8.2
pillow==11.3.0
python-dotenv==1.1.1
pytz==2025.2
email-validator==2.2.0
pydantic==2.11.7
EOF

# Create startup script
cat > "$DEPLOY_DIR/start_backend.sh" <<'EOF'
#!/bin/bash
cd /var/www/html/bramkamvp/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
EOF
chmod +x "$DEPLOY_DIR/start_backend.sh"

# Create systemd service file for backend
cat > "$DEPLOY_DIR/bramkamvp-backend.service" <<EOF
[Unit]
Description=BramkaMVP Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/html/bramkamvp/backend
Environment="PATH=/var/www/html/bramkamvp/backend/venv/bin"
ExecStart=/var/www/html/bramkamvp/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
cat > "$DEPLOY_DIR/nginx-bramkamvp.conf" <<'EOF'
# Nginx configuration for bramkamvp
location /bramkamvp {
    alias /var/www/html/bramkamvp/frontend_dist;
    try_files $uri $uri/ /bramkamvp/index.html;
}

location /bramkamvp/api {
    proxy_pass http://localhost:8000/api;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /bramkamvp/assets {
    alias /var/www/html/bramkamvp/backend/static;
}
EOF

# Create deployment instructions
cat > "$DEPLOY_DIR/DEPLOY_INSTRUCTIONS.md" <<'EOF'
# Deployment Instructions

## 1. Upload files to server
```bash
scp -r * vizi@borgtools.ddns.net:/tmp/bramkamvp_deploy/
```

## 2. SSH to server
```bash
ssh vizi@borgtools.ddns.net
```

## 3. On the server, run:
```bash
# Stop existing services
sudo systemctl stop bramkamvp-backend 2>/dev/null || true

# Clean old installation
sudo rm -rf /var/www/html/bramkamvp

# Create new directory
sudo mkdir -p /var/www/html/bramkamvp

# Copy files
sudo cp -r /tmp/bramkamvp_deploy/* /var/www/html/bramkamvp/

# Setup Python virtual environment
cd /var/www/html/bramkamvp/backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt

# Create data directory
mkdir -p data

# Set permissions
sudo chown -R www-data:www-data /var/www/html/bramkamvp

# Install systemd service
sudo cp /var/www/html/bramkamvp/bramkamvp-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bramkamvp-backend
sudo systemctl start bramkamvp-backend

# Update nginx configuration
sudo cp /var/www/html/bramkamvp/nginx-bramkamvp.conf /etc/nginx/sites-available/borgos-bramkamvp
# Manual step: Include this in main nginx config

# Reload nginx
sudo nginx -t && sudo systemctl reload nginx

# Check status
sudo systemctl status bramkamvp-backend
```

## 4. Test the deployment
- Frontend: https://borgtools.ddns.net/bramkamvp/
- Backend API: https://borgtools.ddns.net/bramkamvp/api/organization
- Test payment: https://borgtools.ddns.net/bramkamvp/goal/church
EOF

# Create archive
echo -e "${YELLOW}📦 Creating deployment archive...${NC}"
cd "$DEPLOY_DIR"
tar -czf /tmp/bramkamvp_production.tar.gz *

echo -e "${GREEN}✅ Deployment package created: /tmp/bramkamvp_production.tar.gz${NC}"
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Upload to server: scp /tmp/bramkamvp_production.tar.gz vizi@borgtools.ddns.net:/tmp/"
echo "2. SSH to server: ssh vizi@borgtools.ddns.net"
echo "3. Extract and deploy: tar -xzf /tmp/bramkamvp_production.tar.gz -C /tmp/deploy && follow DEPLOY_INSTRUCTIONS.md"

# Cleanup
rm -rf "$DEPLOY_DIR"

echo -e "${GREEN}✅ Deployment preparation complete!${NC}"
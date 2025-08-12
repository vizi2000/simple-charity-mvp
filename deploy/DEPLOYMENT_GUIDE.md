# Deployment Guide for Simple Payment Gate

## Server Requirements
- **Target Server**: 192.168.100.159
- **Domain**: simplepaymentgate
- **OS**: Ubuntu 20.04+ or Debian 10+
- **Python**: 3.8+
- **Node.js**: 16+
- **Nginx**: Latest stable
- **RAM**: Minimum 2GB
- **Storage**: Minimum 10GB

## Quick Deployment

### Option 1: Automated Deployment Script
```bash
# From your local machine
cd "/Users/wojciechwiesner/ai/simple mvp charity"
./deploy/deploy.sh
```

### Option 2: Manual Deployment

#### Step 1: Connect to Server
```bash
ssh root@192.168.100.159
```

#### Step 2: Install Dependencies
```bash
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx nodejs npm git
```

#### Step 3: Copy Project Files
```bash
# From local machine
cd "/Users/wojciechwiesner/ai/simple mvp charity"
rsync -avz --exclude 'node_modules' --exclude 'venv*' --exclude '*.log' \
  --exclude '__pycache__' --exclude '.git' \
  backend frontend root@192.168.100.159:/var/www/simplepaymentgate/
```

#### Step 4: Setup Backend
```bash
# On server
cd /var/www/simplepaymentgate/backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

#### Step 5: Setup Frontend
```bash
cd /var/www/simplepaymentgate/frontend
npm install
npm run build
```

#### Step 6: Configure Nginx
```bash
# Copy nginx config
cp /path/to/deploy/nginx.conf /etc/nginx/sites-available/simplepaymentgate
ln -s /etc/nginx/sites-available/simplepaymentgate /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

#### Step 7: Setup Systemd Service
```bash
# Copy service file
cp /path/to/deploy/backend.service /etc/systemd/system/simplepaymentgate-backend.service
systemctl daemon-reload
systemctl enable simplepaymentgate-backend
systemctl start simplepaymentgate-backend
```

#### Step 8: Configure Environment
```bash
# Copy production environment file
cp /path/to/deploy/.env.production /var/www/simplepaymentgate/.env

# Edit with your production values
nano /var/www/simplepaymentgate/.env
```

## Post-Deployment Configuration

### 1. Update Frontend API URL
Edit `/var/www/simplepaymentgate/frontend/src/utils/api.js`:
```javascript
const API_URL = 'http://192.168.100.159/api';
// or 'https://simplepaymentgate/api' when domain is configured
```

### 2. Configure Fiserv Webhook URL
Update Fiserv dashboard to point webhooks to:
```
http://192.168.100.159/api/webhooks/fiserv
```

### 3. Set Proper Permissions
```bash
chown -R www-data:www-data /var/www/simplepaymentgate
chmod -R 755 /var/www/simplepaymentgate
chmod -R 777 /var/www/simplepaymentgate/backend/app/data
chmod -R 777 /var/www/simplepaymentgate/backend/static/uploads
```

### 4. Configure DNS (Optional)
Add DNS A record:
```
simplepaymentgate -> 192.168.100.159
```

Or add to local hosts file:
```bash
echo "192.168.100.159 simplepaymentgate" >> /etc/hosts
```

### 5. SSL Certificate (Recommended for Production)
```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d simplepaymentgate

# Auto-renewal
systemctl enable certbot.timer
```

## Monitoring & Maintenance

### Check Service Status
```bash
systemctl status simplepaymentgate-backend
systemctl status nginx
```

### View Logs
```bash
# Backend logs
tail -f /var/log/simplepaymentgate/backend.log
tail -f /var/log/simplepaymentgate/backend-error.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
systemctl restart simplepaymentgate-backend
systemctl restart nginx
```

### Update Application
```bash
# Pull latest changes
cd /var/www/simplepaymentgate
git pull

# Rebuild frontend
cd frontend
npm install
npm run build

# Restart backend
systemctl restart simplepaymentgate-backend
```

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
journalctl -u simplepaymentgate-backend -n 50

# Test manually
cd /var/www/simplepaymentgate/backend
./venv/bin/python main.py
```

### Payment Gateway Issues
1. Verify Fiserv credentials in `.env`
2. Check timezone is set to `Europe/Warsaw`
3. Ensure webhook URL is accessible from internet
4. Test with Fiserv test cards

### Frontend Not Loading
1. Check nginx configuration: `nginx -t`
2. Verify frontend build: `ls -la /var/www/simplepaymentgate/frontend/dist`
3. Check browser console for errors

## Security Checklist

- [ ] Change default SECRET_KEY in .env
- [ ] Set strong JWT_SECRET
- [ ] Configure firewall (ufw)
- [ ] Enable SSL/HTTPS
- [ ] Restrict SSH access
- [ ] Regular security updates: `apt-get update && apt-get upgrade`
- [ ] Setup fail2ban for brute force protection
- [ ] Configure log rotation

## Backup Strategy

### Daily Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backups/simplepaymentgate"
DATE=$(date +%Y%m%d)

# Backup data files
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /var/www/simplepaymentgate/backend/app/data

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/simplepaymentgate/backend/static/uploads

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## Support Contacts

For issues with:
- **Fiserv Integration**: Check FISERV_TEST_CARDS.md in backend directory
- **Payment Processing**: Review payment_info_*.json files in data directory
- **Application Errors**: Check logs in /var/log/simplepaymentgate/

## Production Checklist

Before going live:
- [ ] SSL certificate installed
- [ ] Production Fiserv credentials configured
- [ ] Backup system in place
- [ ] Monitoring configured
- [ ] Security hardening completed
- [ ] Load testing performed
- [ ] DNS properly configured
- [ ] Email notifications working
- [ ] Error tracking setup
- [ ] Documentation updated
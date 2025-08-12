# 🎉 Deployment Successful!

Your Simple Payment Gate charity application has been successfully deployed to **192.168.100.159**

## Access Points

- **Application URL**: http://192.168.100.159
- **API Endpoint**: http://192.168.100.159/api/
- **Organization Data**: http://192.168.100.159/api/organization

## Services Status

✅ **Backend Service**: Running on port 8000 (simplepaymentgate-backend.service)
✅ **Nginx**: Running and serving frontend + proxying API
✅ **Frontend**: Built and deployed at /var/www/simplepaymentgate/frontend/dist

## Deployed Components

### Backend (FastAPI)
- Location: `/var/www/simplepaymentgate/backend`
- Python venv: `/var/www/simplepaymentgate/backend/venv`
- Data files: `/var/www/simplepaymentgate/backend/app/data/`
- Environment: `/var/www/simplepaymentgate/.env`

### Frontend (React + Vite)
- Source: `/var/www/simplepaymentgate/frontend`
- Built files: `/var/www/simplepaymentgate/frontend/dist`
- Assets: Served through Nginx

## Management Commands

### Check Service Status
```bash
ssh vizi@192.168.100.159 'sudo systemctl status simplepaymentgate-backend'
ssh vizi@192.168.100.159 'sudo systemctl status nginx'
```

### View Logs
```bash
# Backend logs
ssh vizi@192.168.100.159 'sudo journalctl -u simplepaymentgate-backend -f'

# Nginx access logs
ssh vizi@192.168.100.159 'sudo tail -f /var/log/nginx/access.log'

# Nginx error logs
ssh vizi@192.168.100.159 'sudo tail -f /var/log/nginx/error.log'
```

### Restart Services
```bash
ssh vizi@192.168.100.159 'sudo systemctl restart simplepaymentgate-backend'
ssh vizi@192.168.100.159 'sudo systemctl restart nginx'
```

## Next Steps

### 1. Configure Fiserv Webhook
Update your Fiserv dashboard to send webhooks to:
```
http://192.168.100.159/api/webhooks/fiserv
```

### 2. Update DNS (Optional)
Add DNS A record or update hosts file:
```
192.168.100.159 simplepaymentgate
```

### 3. SSL Certificate (Production)
For HTTPS, install SSL certificate:
```bash
ssh vizi@192.168.100.159
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d simplepaymentgate
```

### 4. Update Environment Variables
Edit production settings:
```bash
ssh vizi@192.168.100.159
sudo nano /var/www/simplepaymentgate/.env
```

Key variables to update:
- `FISERV_API_KEY` - Production API key
- `FISERV_API_SECRET` - Production secret
- `SECRET_KEY` - Change from default
- `JWT_SECRET` - Change from default

### 5. Test Payment Flow
1. Visit http://192.168.100.159
2. Select a donation goal
3. Enter amount and proceed to payment
4. Test with Fiserv test cards

## Troubleshooting

### If services fail to start
```bash
# Check detailed error logs
ssh vizi@192.168.100.159 'sudo journalctl -xe'

# Test backend manually
ssh vizi@192.168.100.159
cd /var/www/simplepaymentgate/backend
sudo -u www-data ./venv/bin/python main.py
```

### If frontend doesn't load
```bash
# Check nginx configuration
ssh vizi@192.168.100.159 'sudo nginx -t'

# Verify frontend build
ssh vizi@192.168.100.159 'ls -la /var/www/simplepaymentgate/frontend/dist'
```

### Payment Gateway Issues
- Verify Fiserv credentials in `.env`
- Check timezone is `Europe/Warsaw`
- Ensure webhook URL is accessible
- Review payment logs in backend

## Backup

To backup data:
```bash
ssh vizi@192.168.100.159 'sudo tar -czf backup_$(date +%Y%m%d).tar.gz /var/www/simplepaymentgate/backend/app/data'
```

## Update Deployment

To update the application:
```bash
# From local machine
cd "/Users/wojciechwiesner/ai/simple mvp charity"
./deploy/quick_deploy.sh

# Or manually
ssh vizi@192.168.100.159
cd /var/www/simplepaymentgate
# Update code...
sudo systemctl restart simplepaymentgate-backend
```

---

**Deployment completed at**: 2025-08-11 22:23 CEST
**Deployed by**: Claude Code
**Server**: vizi@192.168.100.159
**Application**: Simple Payment Gate - Charity MVP
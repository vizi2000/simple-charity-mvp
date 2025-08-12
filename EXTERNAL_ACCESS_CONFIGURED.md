# ✅ External Access Configured Successfully!

Your charity payment gateway is now accessible from the internet at:
**https://borgtools.ddns.net/bramkamvp**

## Configuration Summary

### Public Access Points
- **Main Application**: https://borgtools.ddns.net/bramkamvp
- **API Endpoint**: https://borgtools.ddns.net/bramkamvp/api/
- **Organization Data**: https://borgtools.ddns.net/bramkamvp/api/organization

### Updated Configuration

#### Nginx
- Added location blocks to borgos site configuration for `/bramkamvp` path
- Configured proxy pass to backend on port 8000
- Set up proper rewrites for API calls
- Assets served with correct paths

#### Backend (FastAPI)
- **CORS Origins Updated** to include:
  - https://borgtools.ddns.net
  - https://test.ipg-online.com (Fiserv gateway)
  - Local development origins
- **Environment Variables**:
  - `FRONTEND_BASE_URL=https://borgtools.ddns.net/bramkamvp`
  - `WEBHOOK_BASE_URL=https://borgtools.ddns.net/bramkamvp`
  - Payment success/failure URLs updated

#### Frontend (React)
- Built with base path `/bramkamvp/`
- API calls configured to use correct subdirectory
- Assets paths updated in build output
- Dynamic API URL detection based on hostname

### Payment Gateway Integration

#### Fiserv Webhook URL
Update your Fiserv dashboard to use:
```
https://borgtools.ddns.net/bramkamvp/api/webhooks/fiserv
```

#### Payment Flow URLs
- **Success**: https://borgtools.ddns.net/bramkamvp/payment/success
- **Failure**: https://borgtools.ddns.net/bramkamvp/payment/failure

### Security Features
- ✅ HTTPS enabled (SSL via Let's Encrypt)
- ✅ CORS properly configured for S2S validation
- ✅ Security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
- ✅ Payment hash validation using HMACSHA256

### Testing the Application

1. **Visit the application**:
   ```
   https://borgtools.ddns.net/bramkamvp
   ```

2. **Test API directly**:
   ```bash
   curl https://borgtools.ddns.net/bramkamvp/api/organization
   ```

3. **Test payment flow**:
   - Select a donation goal
   - Enter amount
   - Complete test payment with Fiserv test cards

### Management Commands

#### Check status from anywhere:
```bash
ssh vizi@192.168.100.159 'sudo systemctl status simplepaymentgate-backend'
```

#### View logs remotely:
```bash
ssh vizi@192.168.100.159 'sudo journalctl -u simplepaymentgate-backend -f'
```

#### Update application:
```bash
# From local machine
cd "/Users/wojciechwiesner/ai/simple mvp charity"
./deploy/quick_deploy.sh
```

### Important Notes

1. **SSL Certificate**: Already configured via Let's Encrypt for borgtools.ddns.net
2. **Subdirectory Routing**: Application runs at `/bramkamvp` path, not root
3. **Shared Server**: Running alongside other applications on borgtools.ddns.net
4. **Port 8000**: Backend API (internal only, proxied through nginx)

### Troubleshooting

If assets don't load:
```bash
# Check nginx logs
ssh vizi@192.168.100.159 'sudo tail -f /var/log/nginx/error.log'

# Verify paths in built files
ssh vizi@192.168.100.159 'grep -r "assets" /var/www/simplepaymentgate/frontend/dist/index.html'
```

If API calls fail:
```bash
# Check CORS headers
curl -I https://borgtools.ddns.net/bramkamvp/api/organization

# Check backend logs
ssh vizi@192.168.100.159 'sudo journalctl -u simplepaymentgate-backend -n 50'
```

---

**Deployment completed**: 2025-08-11 22:30 CEST
**External URL**: https://borgtools.ddns.net/bramkamvp
**SSL**: Active via Let's Encrypt
**Status**: ✅ Fully operational
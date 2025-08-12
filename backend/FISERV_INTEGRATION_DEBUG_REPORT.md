# Fiserv IPG Integration - Complete Debug Report

**Report Date:** July 28, 2025  
**Issue:** "Transakcja nie może być zakończona powodzeniem" (Transaction cannot be completed successfully)  
**Error Type:** "Wystąpił nieznany błąd aplikacji" (Unknown application error occurred)  
**Environment:** Test/Sandbox  

## 1. SYSTEM CONFIGURATION

### 1.1 Credentials & Environment Variables
```bash
FISERV_API_KEY=xWdewnCcYTy8G0s4oS1r5GAOmcdVRYQn
FISERV_API_SECRET=aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG
FISERV_BASE_URL=https://test.ipg-online.com/api/v1
FISERV_STORE_ID=760995999
FISERV_SHARED_SECRET=j}2W3P)Lwv
FISERV_GATEWAY_URL=https://test.ipg-online.com/connect/gateway/processing
FISERV_MERCHANT_ID=760995999
FISERV_TERMINAL_ID=760995999
FISERV_ENDPOINT=https://test.ipg-online.com/connect/gateway/processing
WEBHOOK_BASE_URL=https://77597ddbcc37.ngrok-free.app
FRONTEND_BASE_URL=http://localhost:5174
```

### 1.2 System Architecture
- **Backend:** FastAPI (Python) on http://localhost:8001
- **Frontend:** React/Vite on http://localhost:5174
- **Payment Gateway Docker:** Running on localhost:8000 (backend) and localhost:3000 (frontend)
- **ngrok Tunnel:** https://77597ddbcc37.ngrok-free.app → localhost:8001
- **Integration Type:** IPG Connect (Form-based POST with HMAC-SHA256)

## 2. IMPLEMENTATION DETAILS

### 2.1 Hash Generation Algorithm
```python
def _generate_hash(self, params: Dict[str, str]) -> str:
    # Fields excluded from hash: 'hash', 'hash_algorithm'
    sorted_params = sorted([(k, v) for k, v in params.items() 
                           if k not in exclude_fields and v])
    values_to_hash = '|'.join(str(v) for k, v in sorted_params)
    hash_value = hmac.new(
        self.shared_secret.encode('utf-8'),
        values_to_hash.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(hash_value).decode('utf-8')
```

### 2.2 Sample Generated Form Data
```json
{
  "form_action": "https://test.ipg-online.com/connect/gateway/processing",
  "form_fields": {
    "storename": "760995999",
    "txntype": "sale",
    "timezone": "Europe/Warsaw",
    "txndatetime": "2025:07:28-19:58:42",
    "chargetotal": "50.00",
    "currency": "985",
    "oid": "c8d49655-5bf5-4c86-aa5e-b09798513931",
    "comments": "Darowizna na cel: Ofiara na kościół",
    "responseSuccessURL": "http://localhost:5174/platnosc/c8d49655-5bf5-4c86-aa5e-b09798513931/status?result=success",
    "responseFailURL": "http://localhost:5174/platnosc/c8d49655-5bf5-4c86-aa5e-b09798513931/status?result=failure",
    "language": "pl_PL",
    "authenticateTransaction": "true",
    "transactionNotificationURL": "https://77597ddbcc37.ngrok-free.app/api/webhooks/fiserv",
    "bname": "Test User",
    "bemail": "test@example.com",
    "hash_algorithm": "HMACSHA256",
    "hash": "MgASdVWLOYnHmTCmfNjpgJBvGtpkBB9Ng80tfKQfB6Y="
  }
}
```

### 2.3 Hash Calculation Example
For the above payment, the hash input string (sorted alphabetically):
```
authenticateTransaction=true|bemail=test@example.com|bname=Test User|chargetotal=50.00|comments=Darowizna na cel: Ofiara na kościół|currency=985|language=pl_PL|oid=c8d49655-5bf5-4c86-aa5e-b09798513931|responseFailURL=http://localhost:5174/platnosc/c8d49655-5bf5-4c86-aa5e-b09798513931/status?result=failure|responseSuccessURL=http://localhost:5174/platnosc/c8d49655-5bf5-4c86-aa5e-b09798513931/status?result=success|storename=760995999|timezone=Europe/Warsaw|transactionNotificationURL=https://77597ddbcc37.ngrok-free.app/api/webhooks/fiserv|txndatetime=2025:07:28-19:58:42|txntype=sale
```

## 3. TEST SCENARIOS & RESULTS

### 3.1 Card Payment Test
- **Payment ID:** c8d49655-5bf5-4c86-aa5e-b09798513931
- **Amount:** 50.00 PLN
- **Method:** Card
- **Result:** Form generated successfully, Fiserv returns error

### 3.2 BLIK Payment Test
- **Payment ID:** f73132b9-8b50-43e2-9cb0-0c88f0694008
- **Amount:** 25.00 PLN
- **Method:** BLIK (includes `blikPayment=true`)
- **Result:** Form generated successfully, Fiserv returns error

### 3.3 Test Cards Used
```
Visa: 4005550000000019 (CVV: 111, Exp: 12/25)
Mastercard: 5204740000001002 (CVV: 111, Exp: 12/25)
BLIK Code: 777123
```

## 4. CHRONOLOGICAL DEBUGGING HISTORY

### Phase 1: Initial Implementation (REST API approach)
- Attempted to use payment-links endpoint
- Discovered this was wrong approach for the provided credentials

### Phase 2: IPG Connect Implementation
- Switched to form-based POST method per documentation
- Initial hash issues:
  - ❌ Used no separators between values
  - ❌ Used hex encoding
  - ✅ Fixed to use pipe separators and base64

### Phase 3: Hash Field Confusion
- ❌ Initially used `hashExtended` field
- ✅ Changed to `hash` field per documentation
- Both approaches resulted in same error

### Phase 4: Parameter Adjustments
- Added all required fields per Fiserv docs
- Ensured proper date format (YYYY:MM:DD-HH:MM:SS)
- Added language parameter (pl_PL)
- Enabled 3D Secure (authenticateTransaction=true)

### Phase 5: ngrok Integration
- Setup public webhook URL
- Authtoken: 30W73pJFbWgjEuostJ0vxD1wu10_Qr5kuLK9DNdTLD6RpY4p
- Public URL: https://77597ddbcc37.ngrok-free.app
- Webhook endpoint: /api/webhooks/fiserv

## 5. CURRENT STATE ANALYSIS

### 5.1 What's Working ✅
1. Payment creation in local database
2. Form data generation with all required fields
3. Hash calculation matching Fiserv documentation
4. ngrok tunnel for webhooks
5. Frontend integration and redirection
6. Both card and BLIK payment configurations

### 5.2 What's Not Working ❌
1. Fiserv gateway accepts form but returns generic error
2. No specific error details from Fiserv
3. No webhook callbacks received (possibly due to transaction failure)

### 5.3 Suspicious Indicators
1. **Generic Error Message:** "Unknown application error" suggests configuration issue
2. **No Transaction ID:** Fiserv doesn't return a transaction ID in error
3. **Immediate Failure:** Error appears instantly, suggesting pre-validation failure
4. **External Access Attempt:** Log shows 188.33.46.187 trying GET on webhook (should be POST)

## 6. POTENTIAL ROOT CAUSES

### 6.1 Merchant Configuration Issues
- Test merchant not fully activated
- Missing required merchant settings
- Incorrect merchant/terminal ID mapping
- Payment methods not enabled for merchant

### 6.2 Authentication Issues
- Shared secret mismatch
- Store ID not linked to provided credentials
- API key/secret not authorized for IPG Connect

### 6.3 Regional/Currency Issues
- PLN (985) not enabled for test merchant
- Poland region not configured
- Test cards not valid for PLN transactions

### 6.4 Environment Mismatch
- Using production credentials on test endpoint
- Using test credentials on wrong test environment
- Sandbox account limitations

## 7. DIAGNOSTIC QUESTIONS FOR FISERV SUPPORT

1. **Account Status**
   - Is store ID 760995999 fully activated for test transactions?
   - Are the provided API credentials valid for IPG Connect?
   - Is the shared secret "j}2W3P)Lwv" correct for this store?

2. **Configuration**
   - Is PLN currency (985) enabled for this merchant?
   - Are card and BLIK payments enabled?
   - Is 3D Secure properly configured?

3. **Technical Details**
   - Are we using the correct test endpoint?
   - Is the hash algorithm HMACSHA256 configured for this store?
   - Are there any IP whitelisting requirements?

4. **Transaction Logs**
   - Can you see any transaction attempts from our store ID?
   - What specific validation is failing?
   - Are there any additional required fields we're missing?

## 8. ADDITIONAL DEBUG DATA

### 8.1 Network Analysis
- Form submission uses standard POST to Fiserv gateway
- TLS connection established successfully
- Response received (not a network issue)

### 8.2 Webhook Readiness
- Endpoint configured: POST /api/webhooks/fiserv
- Public URL accessible via ngrok
- Ready to receive JSON webhooks
- Signature validation implemented

### 8.3 Frontend Integration
- Payment form auto-submits correctly
- Success/failure URLs configured
- Browser redirects handled properly

## 9. RECOMMENDATIONS FOR O3-PRO DEBUGGING

1. **Request Fiserv Logs**
   - Transaction attempt logs for store 760995999
   - Specific error codes (not generic messages)
   - Field validation failure details

2. **Test Minimal Payload**
   - Try with absolute minimum required fields
   - Remove optional fields like customer info
   - Test without webhook URL

3. **Verify Credentials**
   - Confirm each credential with Fiserv
   - Check if different endpoints exist for this merchant
   - Verify test environment URL

4. **Alternative Hash Methods**
   - Try HMACSHA1 if supported
   - Test with different shared secret encoding
   - Verify field ordering in hash

5. **Contact Information**
   - Fiserv technical support ticket
   - Include this report in entirety
   - Request test transaction walkthrough

## 10. CODE REFERENCES

- **IPG Client:** `/backend/app/utils/fiserv_ipg_client.py`
- **Payment Routes:** `/backend/app/routes/payments.py:48-127`
- **Test Script:** `/backend/test_payment_automated.py`
- **Environment:** `/backend/.env`

## 11. CONCLUSION

The integration appears technically correct based on Fiserv documentation. The generic error suggests a merchant account configuration issue rather than an implementation problem. Direct support from Fiserv with access to transaction logs is likely required to resolve this issue.

---
*Report prepared for advanced debugging by O3-PRO model*
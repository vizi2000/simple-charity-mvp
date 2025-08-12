#!/bin/bash

echo "======================================="
echo "Backend Update Script - HMAC-SHA256 Fix"
echo "======================================="

# Check if running on server
if [ ! -d "/home/wojtek/charity-mvp" ]; then
    echo "Error: This script must be run on the server (192.168.100.159)"
    echo "Directory /home/wojtek/charity-mvp not found"
    exit 1
fi

cd /home/wojtek/charity-mvp/backend

echo ""
echo "1. Creating backup..."
sudo cp app/routes/payments_working.py app/routes/payments_working.py.backup_$(date +%Y%m%d_%H%M%S)

echo ""
echo "2. Updating payments_working.py with HMAC-SHA256 fix..."

# Create the corrected file
cat > /tmp/payments_working_fixed.py << 'EOF'
from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import hashlib
import hmac
import uuid
import json
import os
import pytz
from decimal import Decimal

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Fiserv Configuration
FISERV_CONFIG = {
    "gateway_url": "https://test.ipg-online.com/connect/gateway/processing",
    "storename": "760995999",
    "shared_secret": "j}2W3P)Lwv",
    "currency": "985",  # PLN
    "timezone": "Europe/Warsaw",
    "response_success_url": "https://borgtools.ddns.net/bramkamvp/payment/success",
    "response_fail_url": "https://borgtools.ddns.net/bramkamvp/payment/failure",
    "transaction_notification_url": "https://borgtools.ddns.net/bramkamvp/api/payments/webhooks/fiserv/s2s"
}

# Storage directory
PAYMENTS_DIR = "data/payments"
os.makedirs(PAYMENTS_DIR, exist_ok=True)

class PaymentInitiateRequest(BaseModel):
    amount: float
    organization_id: str
    goal_id: str
    donor_name: Optional[str] = None
    donor_email: Optional[EmailStr] = None
    donor_phone: Optional[str] = None
    message: Optional[str] = None
    is_anonymous: Optional[bool] = False

class PaymentWebhookData(BaseModel):
    status: str
    oid: Optional[str] = None
    txndatetime: Optional[str] = None
    approval_code: Optional[str] = None
    chargetotal: Optional[str] = None

def generate_hash_fiserv_method(storename: str, txndatetime: str, chargetotal: str, currency: str, shared_secret: str) -> str:
    """
    Generate HMAC-SHA256 hash for Fiserv:
    1. Create data string: storename + txndatetime + chargetotal + currency (NO sharedSecret!)
    2. Use sharedSecret as HMAC key
    3. Return hex digest
    """
    data_to_sign = f"{storename}{txndatetime}{chargetotal}{currency}"
    
    hash_obj = hmac.new(
        shared_secret.encode('utf-8'),  # Key
        data_to_sign.encode('utf-8'),   # Data
        hashlib.sha256
    )
    
    hash_value = hash_obj.hexdigest()
    return hash_value

@router.post("/initiate")
async def initiate_payment(request: PaymentInitiateRequest):
    """Initiate a payment with Fiserv"""
    try:
        # Generate unique payment ID
        payment_id = str(uuid.uuid4())
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{payment_id[:8]}"
        
        # Format amount with 2 decimal places
        amount_str = f"{request.amount:.2f}"
        
        # Get current timestamp in Warsaw timezone
        warsaw_tz = pytz.timezone(FISERV_CONFIG["timezone"])
        current_time = datetime.now(warsaw_tz)
        txndatetime = current_time.strftime("%Y:%m:%d-%H:%M:%S")
        
        # Generate hash using HMAC-SHA256
        hash_value = generate_hash_fiserv_method(
            FISERV_CONFIG["storename"],
            txndatetime,
            amount_str,
            FISERV_CONFIG["currency"],
            FISERV_CONFIG["shared_secret"]
        )
        
        # Build form data (transactionNotificationURL is NOT in hash!)
        form_data = {
            "txntype": "sale",
            "timezone": FISERV_CONFIG["timezone"],
            "txndatetime": txndatetime,
            "hash_algorithm": "HMACSHA256",
            "hash": hash_value,
            "storename": FISERV_CONFIG["storename"],
            "chargetotal": amount_str,
            "currency": FISERV_CONFIG["currency"],
            "oid": order_id,
            "responseSuccessURL": FISERV_CONFIG["response_success_url"],
            "responseFailURL": FISERV_CONFIG["response_fail_url"],
            "transactionNotificationURL": FISERV_CONFIG["transaction_notification_url"]
        }
        
        # Add optional donor information
        if request.donor_email:
            form_data["bmail"] = request.donor_email
        if request.donor_name and not request.is_anonymous:
            form_data["bname"] = request.donor_name
        
        # Save payment data
        payment_data = {
            "payment_id": payment_id,
            "order_id": order_id,
            "amount": request.amount,
            "organization_id": request.organization_id,
            "goal_id": request.goal_id,
            "donor_name": request.donor_name if not request.is_anonymous else "Anonymous",
            "donor_email": request.donor_email,
            "donor_phone": request.donor_phone,
            "message": request.message,
            "is_anonymous": request.is_anonymous,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "txndatetime": txndatetime,
            "hash": hash_value
        }
        
        # Save to file
        file_path = os.path.join(PAYMENTS_DIR, f"{payment_id}.json")
        with open(file_path, 'w') as f:
            json.dump(payment_data, f, indent=2)
        
        return {
            "payment_id": payment_id,
            "order_id": order_id,
            "form_url": FISERV_CONFIG["gateway_url"],
            "form_data": form_data
        }
        
    except Exception as e:
        print(f"Error initiating payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/fiserv/s2s")
async def handle_fiserv_s2s_webhook(
    status: str = Form(None),
    oid: str = Form(None),
    txndatetime: str = Form(None),
    approval_code: str = Form(None),
    chargetotal: str = Form(None),
    fail_reason: str = Form(None),
    response_hash: str = Form(None),
    notification_hash: str = Form(None),
    processor_response_code: str = Form(None),
    fail_rc: str = Form(None),
    terminal_id: str = Form(None),
    ccbin: str = Form(None),
    cccountry: str = Form(None),
    ccbrand: str = Form(None)
):
    """Handle S2S notification from Fiserv - MUST return 200 OK"""
    try:
        print(f"S2S Webhook received - Status: {status}, OrderID: {oid}")
        
        # Log all received data
        webhook_data = {
            "status": status,
            "oid": oid,
            "txndatetime": txndatetime,
            "approval_code": approval_code,
            "chargetotal": chargetotal,
            "fail_reason": fail_reason,
            "response_hash": response_hash,
            "notification_hash": notification_hash,
            "processor_response_code": processor_response_code,
            "fail_rc": fail_rc,
            "terminal_id": terminal_id,
            "ccbin": ccbin,
            "cccountry": cccountry,
            "ccbrand": ccbrand,
            "received_at": datetime.now().isoformat()
        }
        
        # Save webhook data
        webhook_file = os.path.join(PAYMENTS_DIR, f"webhook_{oid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(webhook_file, 'w') as f:
            json.dump(webhook_data, f, indent=2)
        
        # Find and update payment status
        if oid:
            for filename in os.listdir(PAYMENTS_DIR):
                if filename.endswith('.json') and not filename.startswith('webhook_'):
                    file_path = os.path.join(PAYMENTS_DIR, filename)
                    with open(file_path, 'r') as f:
                        payment_data = json.load(f)
                    
                    if payment_data.get('order_id') == oid:
                        # Update payment status
                        payment_data['status'] = status.lower() if status else 'unknown'
                        payment_data['fiserv_response'] = webhook_data
                        payment_data['updated_at'] = datetime.now().isoformat()
                        
                        if status == "APPROVED":
                            payment_data['payment_completed'] = True
                            payment_data['approval_code'] = approval_code
                        elif status in ["DECLINED", "FAILED"]:
                            payment_data['payment_completed'] = False
                            payment_data['fail_reason'] = fail_reason
                            payment_data['fail_rc'] = fail_rc
                        
                        # Save updated payment data
                        with open(file_path, 'w') as f:
                            json.dump(payment_data, f, indent=2)
                        
                        print(f"Payment {payment_data['payment_id']} updated with status: {status}")
                        break
        
        # CRITICAL: Always return 200 OK to Fiserv
        return JSONResponse(
            status_code=200,
            content={"status": "OK"}
        )
        
    except Exception as e:
        print(f"Error in S2S webhook: {str(e)}")
        # Even on error, return 200 OK to prevent Fiserv retries
        return JSONResponse(
            status_code=200,
            content={"status": "OK", "error": str(e)}
        )

@router.get("/status/{payment_id}")
async def get_payment_status(payment_id: str):
    """Get payment status by payment ID"""
    try:
        file_path = os.path.join(PAYMENTS_DIR, f"{payment_id}.json")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Payment not found")
        
        with open(file_path, 'r') as f:
            payment_data = json.load(f)
        
        return payment_data
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
async def get_recent_payments(limit: int = 10):
    """Get recent payments"""
    try:
        payments = []
        for filename in os.listdir(PAYMENTS_DIR):
            if filename.endswith('.json') and not filename.startswith('webhook_'):
                file_path = os.path.join(PAYMENTS_DIR, filename)
                with open(file_path, 'r') as f:
                    payment_data = json.load(f)
                payments.append(payment_data)
        
        # Sort by created_at descending
        payments.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return payments[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
EOF

# Copy the fixed file
sudo cp /tmp/payments_working_fixed.py app/routes/payments_working.py

echo ""
echo "3. Setting correct permissions..."
sudo chown wojtek:wojtek app/routes/payments_working.py
sudo chmod 644 app/routes/payments_working.py

echo ""
echo "4. Restarting backend service..."
sudo systemctl restart charity-backend

echo ""
echo "5. Checking service status..."
sudo systemctl status charity-backend --no-pager | head -15

echo ""
echo "======================================="
echo "Update Complete!"
echo "======================================="
echo ""
echo "The backend has been updated with the correct HMAC-SHA256 implementation."
echo "Test it at: https://borgtools.ddns.net/bramkamvp/"
echo ""
echo "Use test cards:"
echo "  DEBIT: 4410947715337430, 12/26, CVV: 287"
echo "  BLIK: 777777"
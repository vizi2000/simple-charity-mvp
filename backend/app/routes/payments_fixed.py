from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import hashlib
import hmac
import uuid
import json
import os
import pytz
import logging
import base64

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage
PAYMENTS_FILE = "data/payments.json"
os.makedirs(os.path.dirname(PAYMENTS_FILE), exist_ok=True)

def load_payments():
    if os.path.exists(PAYMENTS_FILE):
        with open(PAYMENTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_payments(payments):
    with open(PAYMENTS_FILE, 'w') as f:
        json.dump(payments, f, indent=2)

def generate_hash_all_fields(params: dict, shared_secret: str) -> str:
    """
    Generate HMAC-SHA256 hash for ALL fields (except hash itself)
    1. Sort parameters alphabetically by key
    2. Join values with pipe separator
    3. Use HMAC-SHA256 with shared secret as key
    """
    # Remove hash field if present
    params_to_hash = {k: v for k, v in params.items() if k != 'hash'}
    
    # Sort parameters alphabetically
    sorted_keys = sorted(params_to_hash.keys())
    
    # Join values with pipe separator
    values = [str(params_to_hash[key]) for key in sorted_keys]
    data_to_sign = '|'.join(values)
    
    logger.info(f"Fields in hash (alphabetical): {sorted_keys}")
    logger.info(f"Data to sign: {data_to_sign}")
    
    # Generate HMAC-SHA256
    hash_obj = hmac.new(
        shared_secret.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    )
    
    # Return hex digest
    hash_value = hash_obj.hexdigest()
    logger.info(f"Generated hash: {hash_value}")
    
    return hash_value

class InitiatePaymentRequest(BaseModel):
    goal_id: str
    amount: float = Field(gt=0, le=100000)
    donor_name: Optional[str] = "Anonimowy"
    donor_email: Optional[EmailStr] = None
    donor_phone: Optional[str] = None
    message: Optional[str] = None
    is_anonymous: bool = False
    organization_id: str

@router.post("/initiate")
async def initiate_payment(request: InitiatePaymentRequest):
    """Initiate payment with Fiserv - hash ALL fields"""
    try:
        logger.info(f"Payment initiation request: {request.dict()}")
        
        # Generate unique payment and order IDs
        payment_id = str(uuid.uuid4())
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{payment_id[:8]}"
        
        # Configuration
        shared_secret = 'j}2W3P)Lwv'
        store_id = '760995999'
        
        # Format amount with 2 decimal places
        amount_str = f"{float(request.amount):.2f}"
        
        # Get current Warsaw time
        warsaw_tz = pytz.timezone('Europe/Warsaw')
        now = datetime.now(warsaw_tz)
        txn_datetime = now.strftime('%Y:%m:%d-%H:%M:%S')
        
        # Currency code for PLN
        currency = '985'
        
        # Build ALL form fields (except hash)
        form_data = {
            'txntype': 'sale',
            'timezone': 'Europe/Warsaw',
            'txndatetime': txn_datetime,
            'hash_algorithm': 'HMACSHA256',
            'storename': store_id,
            'chargetotal': amount_str,
            'currency': currency,
            'checkoutoption': 'combinedpage',
            'oid': order_id,
            'responseSuccessURL': 'https://borgtools.ddns.net/bramkamvp/payment/success',
            'responseFailURL': 'https://borgtools.ddns.net/bramkamvp/payment/failure',
            'transactionNotificationURL': 'https://borgtools.ddns.net/bramkamvp/api/payments/webhooks/fiserv/s2s'
        }
        
        # Add optional customer data
        if not request.is_anonymous and request.donor_email:
            form_data['bmail'] = request.donor_email
            if request.donor_name:
                form_data['bname'] = request.donor_name
        
        # Generate hash for ALL fields
        hash_value = generate_hash_all_fields(form_data, shared_secret)
        
        # Add hash to form data
        form_data['hash'] = hash_value
        
        # Create payment record
        payment = {
            'payment_id': payment_id,
            'order_id': order_id,
            'goal_id': request.goal_id,
            'amount': request.amount,
            'donor_name': request.donor_name,
            'donor_email': request.donor_email,
            'message': request.message,
            'is_anonymous': request.is_anonymous,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'txn_datetime': txn_datetime
        }
        
        # Save payment
        payments = load_payments()
        payments.append(payment)
        save_payments(payments)
        
        logger.info(f"Payment initiated successfully: {payment_id}")
        logger.info(f"Form data fields: {list(form_data.keys())}")
        logger.info(f"Hash generated from ALL fields")
        
        # Return form data for frontend to submit
        return {
            'payment_id': payment_id,
            'order_id': order_id,
            'form_url': 'https://test.ipg-online.com/connect/gateway/processing',
            'form_data': form_data
        }
        
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Payment initiation failed: {str(e)}")

@router.post("/webhooks/fiserv/s2s")
async def handle_fiserv_s2s_webhook(
    status: str = Form(None),
    oid: str = Form(None),
    txndatetime: str = Form(None),
    approval_code: str = Form(None),
    chargetotal: str = Form(None),
    fail_reason: str = Form(None),
    response_hash: str = Form(None),
    notification_hash: str = Form(None)
):
    """Handle S2S webhook from Fiserv"""
    try:
        logger.info(f"S2S Webhook received - Status: {status}, OrderID: {oid}")
        
        # Update payment status
        payments = load_payments()
        for payment in payments:
            if payment.get('order_id') == oid:
                payment['status'] = status.lower() if status else 'unknown'
                payment['webhook_received'] = datetime.now().isoformat()
                if status == "APPROVED":
                    payment['approval_code'] = approval_code
                save_payments(payments)
                break
        
        # MUST return 200 OK
        return JSONResponse(
            status_code=200,
            content={"status": "OK"}
        )
        
    except Exception as e:
        logger.error(f"S2S webhook error: {str(e)}")
        # Still return 200 to prevent retries
        return JSONResponse(
            status_code=200,
            content={"status": "OK", "error": str(e)}
        )

@router.get("/status/{payment_id}")
async def get_payment_status(payment_id: str):
    """Get payment status"""
    payments = load_payments()
    for payment in payments:
        if payment['payment_id'] == payment_id:
            return payment
    raise HTTPException(status_code=404, detail="Payment not found")
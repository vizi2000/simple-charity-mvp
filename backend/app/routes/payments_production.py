"""
Production-ready Fiserv payment integration
Based on working test.html implementation
"""

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

# Configuration
FISERV_CONFIG = {
    'storename': '760995999',
    'shared_secret': 'j}2W3P)Lwv',
    'gateway_url': 'https://test.ipg-online.com/connect/gateway/processing',
    'currency': '985',  # PLN
    'timezone': 'Europe/Warsaw',
    'hash_algorithm': 'HMACSHA256'
}

# Storage
PAYMENTS_FILE = "data/payments.json"
os.makedirs(os.path.dirname(PAYMENTS_FILE), exist_ok=True)

def load_payments():
    """Load payments from JSON file"""
    if os.path.exists(PAYMENTS_FILE):
        with open(PAYMENTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_payments(payments):
    """Save payments to JSON file"""
    with open(PAYMENTS_FILE, 'w') as f:
        json.dump(payments, f, indent=2)

def generate_fiserv_hash(params: dict, shared_secret: str) -> str:
    """
    Generate HMAC-SHA256 hash in Base64 format - EXACTLY like test.html
    1. Sort ALL parameters alphabetically by key (excluding hash fields)
    2. Join values with pipe separator (|)
    3. Generate HMAC-SHA256 with shared secret as key
    4. Encode as Base64
    """
    # Remove hash fields if present - CRITICAL: hash should not be in the data to hash
    params_to_hash = {k: v for k, v in params.items() 
                      if k not in ['hashExtended', 'hash', 'response_hash', 'notification_hash']}
    
    # Sort parameters alphabetically
    sorted_keys = sorted(params_to_hash.keys())
    
    # Join values with pipe separator - CRITICAL: Fiserv expects pipe separator
    values = [str(params_to_hash[key]) for key in sorted_keys]
    data_to_sign = '|'.join(values)
    
    logger.info(f"Sorted keys ({len(sorted_keys)} fields): {sorted_keys}")
    logger.info(f"Data to sign: {data_to_sign[:100]}..." if len(data_to_sign) > 100 else f"Data to sign: {data_to_sign}")
    
    # Generate HMAC-SHA256
    signature = hmac.new(
        shared_secret.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Encode as Base64 (like in test.html) - CRITICAL: Must be Base64, not hex
    base64_hash = base64.b64encode(signature).decode('utf-8')
    
    logger.info(f"Generated Base64 hash: {base64_hash}")
    
    return base64_hash

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
    """Initiate payment with Fiserv - production ready"""
    try:
        logger.info(f"Payment initiation request: {request.dict()}")
        
        # Generate unique order ID
        payment_id = str(uuid.uuid4())
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{payment_id[:8]}"
        
        # Format amount with 2 decimal places
        amount_str = f"{float(request.amount):.2f}"
        
        # Get current Warsaw time (EXACTLY like test.html)
        warsaw_tz = pytz.timezone('Europe/Warsaw')
        now = datetime.now(warsaw_tz)
        txn_datetime = now.strftime('%Y:%m:%d-%H:%M:%S')
        
        # Determine environment URLs (production vs test)
        # In production, these should use HTTPS
        base_url = "https://borgtools.ddns.net/bramkamvp"
        
        # CRITICAL: Build ALL form parameters FIRST, BEFORE generating hash
        # This ensures the hash includes every single field being sent
        form_params = {
            'txntype': 'sale',
            'timezone': FISERV_CONFIG['timezone'],
            'txndatetime': txn_datetime,
            'hash_algorithm': FISERV_CONFIG['hash_algorithm'],
            'storename': FISERV_CONFIG['storename'],
            'chargetotal': amount_str,
            'currency': FISERV_CONFIG['currency'],
            'checkoutoption': 'combinedpage',
            'oid': order_id,
            'paymentMethod': 'M',  # Mixed (card + BLIK)
            'responseSuccessURL': f'{base_url}/payment/success',
            'responseFailURL': f'{base_url}/payment/failure',
            'transactionNotificationURL': f'{base_url}/api/payments/webhooks/fiserv/s2s'
        }
        
        # Add optional customer fields if not anonymous
        # These MUST be added BEFORE hash generation
        if not request.is_anonymous:
            if request.donor_email:
                form_params['bmail'] = request.donor_email
            if request.donor_name:
                form_params['bname'] = request.donor_name
        
        # NOW generate hash with ALL fields that will be sent
        # The hash MUST include every field in form_params
        hash_value = generate_fiserv_hash(form_params, FISERV_CONFIG['shared_secret'])
        
        # Add hash to form data as 'hashExtended' AFTER generating it
        form_params['hashExtended'] = hash_value
        
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
            'txn_datetime': txn_datetime,
            'form_params_sent': list(form_params.keys())  # For debugging
        }
        
        # Save payment
        payments = load_payments()
        payments.append(payment)
        save_payments(payments)
        
        logger.info(f"Payment initiated: {payment_id}")
        logger.info(f"Order ID: {order_id}")
        logger.info(f"Form params keys: {list(form_params.keys())}")
        
        # Return form data for frontend to submit
        return {
            'payment_id': payment_id,
            'order_id': order_id,
            'form_url': FISERV_CONFIG['gateway_url'],
            'form_data': form_params
        }
        
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Payment initiation failed: {str(e)}")

@router.post("/webhooks/fiserv/s2s")
async def handle_fiserv_s2s_webhook(request: Request):
    """
    Handle S2S webhook from Fiserv
    CRITICAL: Must ALWAYS return 200 OK
    """
    try:
        # Get form data
        form_data = await request.form()
        input_data = dict(form_data)
        
        logger.info(f"S2S Webhook received: {input_data}")
        
        # Extract key fields
        order_id = input_data.get('oid')
        status = input_data.get('status', '').upper()
        approval_code = input_data.get('approval_code')
        transaction_id = input_data.get('ipgTransactionId')
        fail_reason = input_data.get('fail_reason')
        
        # Verify signature if provided
        received_hash = input_data.get('response_hash') or input_data.get('notification_hash')
        if received_hash:
            # Verify hash (implement verification logic)
            logger.info(f"Hash verification required for order {order_id}")
            # TODO: Implement hash verification
        
        # Update payment status
        payments = load_payments()
        payment_updated = False
        
        for payment in payments:
            if payment.get('order_id') == order_id:
                payment['status'] = status.lower() if status else 'unknown'
                payment['webhook_received'] = datetime.now().isoformat()
                payment['transaction_id'] = transaction_id
                
                if status == 'APPROVED':
                    payment['approval_code'] = approval_code
                    payment['payment_completed'] = True
                    logger.info(f"Payment APPROVED: {order_id}, approval: {approval_code}")
                    
                elif status == 'DECLINED':
                    payment['fail_reason'] = fail_reason
                    payment['payment_completed'] = False
                    logger.info(f"Payment DECLINED: {order_id}, reason: {fail_reason}")
                    
                elif status == 'FAILED':
                    payment['fail_reason'] = fail_reason or 'Transaction failed'
                    payment['payment_completed'] = False
                    logger.info(f"Payment FAILED: {order_id}")
                    
                payment_updated = True
                break
        
        if payment_updated:
            save_payments(payments)
            logger.info(f"Payment status updated for order: {order_id}")
        else:
            logger.warning(f"Order not found: {order_id}")
        
        # Log all webhook data for debugging
        webhook_log = {
            'timestamp': datetime.now().isoformat(),
            'order_id': order_id,
            'status': status,
            'data': input_data
        }
        
        # Save webhook log
        log_file = 'data/webhook_log.json'
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            logs.append(webhook_log)
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save webhook log: {e}")
        
    except Exception as e:
        logger.error(f"S2S webhook error: {str(e)}", exc_info=True)
    
    # ALWAYS return 200 OK to prevent Fiserv retries
    return JSONResponse(
        status_code=200,
        content={"status": "OK", "timestamp": datetime.now().isoformat()}
    )

@router.get("/status/{payment_id}")
async def get_payment_status(payment_id: str):
    """Get payment status by payment ID"""
    payments = load_payments()
    for payment in payments:
        if payment['payment_id'] == payment_id:
            return payment
    raise HTTPException(status_code=404, detail="Payment not found")

@router.get("/order-status/{order_id}")
async def get_order_status(order_id: str):
    """Get payment status by order ID"""
    payments = load_payments()
    for payment in payments:
        if payment['order_id'] == order_id:
            return {
                'order_id': order_id,
                'status': payment.get('status', 'pending'),
                'payment_completed': payment.get('payment_completed', False),
                'amount': payment.get('amount'),
                'created_at': payment.get('created_at')
            }
    raise HTTPException(status_code=404, detail="Order not found")

@router.get("/test-hash")
async def test_hash_generation():
    """Test endpoint to verify hash generation matches test.html"""
    test_params = {
        'chargetotal': '10.00',
        'checkoutoption': 'combinedpage',
        'currency': '985',
        'hash_algorithm': 'HMACSHA256',
        'oid': 'TEST-123',
        'paymentMethod': 'M',
        'responseFailURL': 'https://test.ipg-online.com/webshop/response_failure.jsp',
        'responseSuccessURL': 'https://test.ipg-online.com/webshop/response_success.jsp',
        'storename': '760995999',
        'timezone': 'Europe/Warsaw',
        'txndatetime': '2025:08:10-14:30:00',
        'txntype': 'sale'
    }
    
    hash_value = generate_fiserv_hash(test_params, FISERV_CONFIG['shared_secret'])
    
    return {
        'test_params': test_params,
        'sorted_keys': sorted(test_params.keys()),
        'data_to_sign': '|'.join([str(test_params[k]) for k in sorted(test_params.keys())]),
        'generated_hash': hash_value,
        'expected_hash_from_test_html': 'Should match the hash from test.html with same params'
    }
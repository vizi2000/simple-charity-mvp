"""
Corrected Payment Routes based on detailed Fiserv guide
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import json
import uuid
import logging
from datetime import datetime
import os
from pathlib import Path
import hashlib
import hmac
import pytz

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Data storage paths  
DATA_PATH = Path(__file__).parent.parent / "data"
PAYMENTS_FILE = DATA_PATH / "payments.json"

def load_payments() -> list:
    """Load payments from JSON file"""
    if PAYMENTS_FILE.exists():
        with open(PAYMENTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_payments(payments: list):
    """Save payments to JSON file"""
    DATA_PATH.mkdir(exist_ok=True)
    with open(PAYMENTS_FILE, 'w') as f:
        json.dump(payments, f, indent=2, default=str)

def generate_hash_fiserv_method(storename: str, txndatetime: str, chargetotal: str, currency: str, shared_secret: str) -> str:
    """
    Generate HMAC-SHA256 hash for Fiserv:
    1. Create data string: storename + txndatetime + chargetotal + currency (NO sharedSecret!)
    2. Use sharedSecret as HMAC key
    3. Return hex digest
    """
    # Create the string to sign (WITHOUT sharedSecret at the end!)
    data_to_sign = f"{storename}{txndatetime}{chargetotal}{currency}"
    
    logger.info(f"Data to sign: {data_to_sign}")
    logger.info(f"Using shared secret as HMAC key: {shared_secret}")
    
    # Use HMAC-SHA256 with sharedSecret as the key
    hash_obj = hmac.new(
        shared_secret.encode('utf-8'),  # Key
        data_to_sign.encode('utf-8'),   # Data
        hashlib.sha256
    )
    
    # Get hex digest
    hash_value = hash_obj.hexdigest()
    
    logger.info(f"Generated HMAC-SHA256 hash: {hash_value}")
    
    return hash_value

class InitiatePaymentRequest(BaseModel):
    goal_id: str
    amount: float = Field(gt=0, le=100000)
    donor_name: Optional[str] = "Anonimowy"
    donor_email: Optional[str] = None
    message: Optional[str] = None
    is_anonymous: bool = False

@router.post("/initiate")
async def initiate_payment(request: InitiatePaymentRequest):
    """
    Initiate payment process - corrected version based on Fiserv guide
    """
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
        
        logger.info(f"Transaction datetime: {txn_datetime}")
        
        # Currency code for PLN
        currency = '985'
        
        # Generate hash using the exact method from guide
        hash_value = generate_hash_fiserv_method(
            storename=store_id,
            txndatetime=txn_datetime,
            chargetotal=amount_str,
            currency=currency,
            shared_secret=shared_secret
        )
        
        # Build form data
        form_data = {
            'txntype': 'sale',
            'timezone': 'Europe/Warsaw',
            'txndatetime': txn_datetime,
            'hash_algorithm': 'HMACSHA256',  # Correct algorithm
            'hash': hash_value,  # HMAC-SHA256 hash
            'storename': store_id,
            'chargetotal': amount_str,
            'currency': currency,
            'checkoutoption': 'combinedpage',  # REQUIRED for combined payment page
            'oid': order_id,
            # Add response URLs
            'responseSuccessURL': 'https://borgtools.ddns.net/bramkamvp/payment/success',
            'responseFailURL': 'https://borgtools.ddns.net/bramkamvp/payment/failure',
            'transactionNotificationURL': 'https://borgtools.ddns.net/bramkamvp/api/payments/webhooks/fiserv/s2s'
        }
        
        # Add customer data if provided
        if not request.is_anonymous and request.donor_email:
            form_data['bmail'] = request.donor_email
            if request.donor_name:
                form_data['bname'] = request.donor_name
        
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

@router.get("/{payment_id}/status")
async def get_payment_status(payment_id: str):
    """Get payment status"""
    payments = load_payments()
    for payment in payments:
        if payment.get('payment_id') == payment_id:
            return {
                'payment_id': payment['payment_id'],
                'status': payment.get('status', 'pending'),
                'amount': payment['amount'],
                'order_id': payment.get('order_id')
            }
    
    raise HTTPException(status_code=404, detail="Payment not found")

@router.post("/webhooks/fiserv/s2s")
async def handle_s2s_notification(request: Request):
    """
    Handle S2S notification from Fiserv
    Always return 200 OK regardless of processing result
    """
    try:
        form_data = await request.form()
        params = dict(form_data)
        
        logger.info(f"S2S notification received: {params}")
        
        # Process the notification
        order_id = params.get('oid')
        status = params.get('status', '').upper()
        
        if order_id:
            # Update payment status
            payments = load_payments()
            for i, payment in enumerate(payments):
                if payment.get('order_id') == order_id:
                    if status == 'APPROVED':
                        payment['status'] = 'completed'
                    elif status == 'DECLINED':
                        payment['status'] = 'failed'
                    elif status == 'CANCELLED':
                        payment['status'] = 'cancelled'
                    
                    payment['fiserv_status'] = status
                    payment['s2s_received_at'] = datetime.now().isoformat()
                    payments[i] = payment
                    break
            
            save_payments(payments)
            logger.info(f"Payment {order_id} updated to status: {status}")
        
        # ALWAYS return 200 OK to Fiserv
        return {"status": "OK"}
        
    except Exception as e:
        logger.error(f"S2S processing error: {str(e)}", exc_info=True)
        # Even on error, return 200 OK to prevent endless retries
        return {"status": "OK"}
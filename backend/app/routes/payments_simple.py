"""
Simplified Payment Routes for debugging
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import json
import uuid
import logging
from datetime import datetime, timezone
import os
from pathlib import Path
import hashlib
import hmac
import base64

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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

def generate_hash(params: dict, shared_secret: str) -> str:
    """Generate HMAC-SHA256 hash for Fiserv payment"""
    # Sort parameters alphabetically by key
    sorted_keys = sorted(params.keys())
    
    # Create string to sign by joining values with pipe separator
    values = [str(params[key]) for key in sorted_keys]
    string_to_sign = '|'.join(values)
    
    # Generate HMAC-SHA256
    signature = hmac.new(
        shared_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Encode in Base64
    return base64.b64encode(signature).decode('utf-8')

class InitiatePaymentRequest(BaseModel):
    goal_id: str
    amount: float = Field(gt=0, le=100000)
    donor_name: Optional[str] = "Anonimowy"
    donor_email: Optional[str] = None
    message: Optional[str] = None
    is_anonymous: bool = False

@router.post("/initiate")
async def initiate_payment(request: InitiatePaymentRequest):
    """Initiate payment process - simplified version"""
    try:
        logger.info(f"Payment initiation request: {request.dict()}")
        
        # Generate unique payment and order IDs
        payment_id = str(uuid.uuid4())
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{payment_id[:8]}"
        
        # Get configuration
        shared_secret = os.getenv('FISERV_API_SECRET', 'j}2W3P)Lwv')
        store_id = os.getenv('FISERV_STORE_ID', '760995999')
        
        # Prepare URLs - without query parameters
        base_url = 'https://borgtools.ddns.net/bramkamvp'
        success_url = f"{base_url}/payment/success"
        fail_url = f"{base_url}/payment/failure"
        notification_url = f"{base_url}/api/payments/webhooks/fiserv/s2s"
        
        # Format amount
        amount_str = f"{float(request.amount):.2f}"
        
        # Get transaction datetime in Warsaw timezone - slightly in the future
        from datetime import datetime, timedelta
        import pytz
        warsaw_tz = pytz.timezone('Europe/Warsaw')
        now = datetime.now(warsaw_tz) + timedelta(minutes=2)  # 2 minutes in the future
        txn_datetime = now.strftime('%Y:%m:%d-%H:%M:%S')
        
        # CRITICAL: Only these fields go into the hash!
        # transactionNotificationURL must NOT be in hash params
        params_for_hash = {
            'chargetotal': amount_str,
            'checkoutoption': 'combinedpage',
            'currency': '985',  # PLN
            'hash_algorithm': 'HMACSHA256',
            'oid': order_id,
            'paymentMethod': 'M',
            'responseFailURL': fail_url,
            'responseSuccessURL': success_url,
            'storename': store_id,
            'timezone': 'Europe/Warsaw',
            'txndatetime': txn_datetime,
            'txntype': 'sale'
        }
        
        # Generate hash ONLY from the above params
        hash_value = generate_hash(params_for_hash, shared_secret)
        
        # Now create the full form data including fields NOT in hash
        params = params_for_hash.copy()
        params['hashExtended'] = hash_value
        params['transactionNotificationURL'] = notification_url  # Add AFTER hash generation!
        
        # Add customer data if not anonymous (these also don't go in hash)
        if not request.is_anonymous and request.donor_email:
            params['bmail'] = request.donor_email
            if request.donor_name:
                params['bname'] = request.donor_name
        
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
            'created_at': datetime.now().isoformat()
        }
        
        # Save payment
        payments = load_payments()
        payments.append(payment)
        save_payments(payments)
        
        logger.info(f"Payment initiated successfully: {payment_id}")
        
        # Return form data for frontend to submit
        return {
            'payment_id': payment_id,
            'order_id': order_id,
            'form_url': 'https://test.ipg-online.com/connect/gateway/processing',
            'form_data': params
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
                'amount': payment['amount']
            }
    
    raise HTTPException(status_code=404, detail="Payment not found")

@router.get("/{payment_id}/verify")
async def verify_payment(payment_id: str):
    """Verify payment status"""
    payments = load_payments()
    
    # Try to find by payment_id or order_id
    payment = None
    for p in payments:
        if p.get('payment_id') == payment_id or p.get('order_id') == payment_id:
            payment = p
            break
    
    if not payment:
        return {'verified': False, 'status': 'not_found'}
    
    status = payment.get('status', 'pending')
    
    return {
        'verified': True,
        'payment_id': payment.get('payment_id'),
        'order_id': payment.get('order_id'),
        'status': status,
        'is_completed': status == 'completed',
        'is_failed': status in ['failed', 'cancelled'],
        'is_pending': status == 'pending',
        'message': get_status_message(status)
    }

def get_status_message(status: str) -> str:
    """Get user-friendly status message"""
    messages = {
        'completed': 'Płatność została pomyślnie zrealizowana',
        'failed': 'Płatność nie powiodła się',
        'cancelled': 'Płatność została anulowana',
        'pending': 'Płatność jest przetwarzana'
    }
    return messages.get(status, 'Status płatności nieznany')

@router.post("/webhooks/fiserv/s2s")
async def handle_s2s_notification(request: Request):
    """Handle S2S notification from Fiserv - simplified"""
    try:
        form_data = await request.form()
        params = dict(form_data)
        
        logger.info(f"S2S notification received: {params}")
        
        # Always return 200 OK to Fiserv
        return {"status": "OK"}
        
    except Exception as e:
        logger.error(f"S2S error: {str(e)}")
        return {"status": "OK"}  # Still return OK
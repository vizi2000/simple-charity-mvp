"""
Secure Payment Routes with Full Fiserv Integration
Based on IMPLEMENTATION_GUIDE.md
"""

from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import uuid
import logging
from datetime import datetime
import os
from pathlib import Path

from ..models import PaymentRequest, Payment, PaymentStatus
from ..utils.fiserv_security import FiservSecurity, FISERV_IP_WHITELIST

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Initialize security handler
security = FiservSecurity(
    shared_secret=os.getenv('FISERV_API_SECRET', 'j}2W3P)Lwv'),
    store_id=os.getenv('FISERV_STORE_ID', '760995999')
)

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

def get_payment_by_id(payment_id: str) -> Optional[Dict]:
    """Get payment by ID"""
    payments = load_payments()
    for payment in payments:
        if payment['payment_id'] == payment_id:
            return payment
    return None

def update_payment(payment_id: str, updates: Dict):
    """Update payment in storage"""
    payments = load_payments()
    for i, payment in enumerate(payments):
        if payment['payment_id'] == payment_id:
            payments[i].update(updates)
            save_payments(payments)
            return payments[i]
    return None

def is_duplicate_notification(order_id: str, transaction_id: str) -> bool:
    """Check if this S2S notification was already processed"""
    payments = load_payments()
    for payment in payments:
        if (payment.get('order_id') == order_id and 
            payment.get('fiserv_transaction_id') == transaction_id and
            payment.get('status') in ['completed', 'failed']):
            return True
    return False

class InitiatePaymentRequest(BaseModel):
    goal_id: str
    amount: float = Field(gt=0, le=100000)
    donor_name: Optional[str] = "Anonimowy"
    donor_email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')  # Email is now required
    message: Optional[str] = None
    is_anonymous: bool = False

@router.post("/initiate")
async def initiate_payment(request: InitiatePaymentRequest):
    """
    Initiate payment process - generates hash on backend
    SECURITY: Never expose shared secret to frontend!
    """
    try:
        # Validate payment data
        validation_errors = security.validate_payment_data(request.dict())
        if validation_errors:
            raise HTTPException(status_code=400, detail={"errors": validation_errors})
        
        # Generate unique payment and order IDs
        payment_id = str(uuid.uuid4())
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{payment_id[:8]}"
        
        # Prepare URLs (use HTTPS in production!)
        base_url = os.getenv('FRONTEND_BASE_URL', 'https://borgtools.ddns.net/bramkamvp')
        webhook_url = os.getenv('WEBHOOK_BASE_URL', 'https://borgtools.ddns.net/bramkamvp')
        
        success_url = f"{base_url}/payment/success?oid={order_id}"
        fail_url = f"{base_url}/payment/failure?oid={order_id}"
        notification_url = f"{webhook_url}/api/webhooks/fiserv/s2s"  # Critical S2S endpoint
        
        # Prepare customer data (email is always required now)
        customer_data = {
            'email': request.donor_email  # Email is required, so it will always be present
        }
        
        # Add name only if not anonymous
        if not request.is_anonymous and request.donor_name:
            customer_data['name'] = request.donor_name
        
        # Generate secure form data with hash
        form_data = security.prepare_payment_form_data(
            amount=request.amount,
            order_id=order_id,
            success_url=success_url,
            fail_url=fail_url,
            notification_url=notification_url,
            customer_data=customer_data
        )
        
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
            'form_data': form_data,
            's2s_notifications': []  # Track all S2S notifications
        }
        
        # Save payment
        payments = load_payments()
        payments.append(payment)
        save_payments(payments)
        
        logger.info(f"Payment initiated: {payment_id} / {order_id}")
        
        # Return form data for frontend to submit
        return {
            'payment_id': payment_id,
            'order_id': order_id,
            'form_url': os.getenv('FISERV_GATEWAY_URL', 'https://test.ipg-online.com/connect/gateway/processing'),
            'form_data': form_data
        }
        
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment initiation failed")

@router.post("/webhooks/fiserv/s2s")
async def handle_s2s_notification(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle Server-to-Server notification from Fiserv
    CRITICAL: This is the ONLY reliable source of payment status!
    
    Security measures:
    1. Verify signature
    2. Check IP whitelist (optional but recommended)
    3. Prevent duplicate processing
    4. ALWAYS return 200 OK
    """
    try:
        # Get client IP
        client_ip = request.client.host
        
        # Optional: Check IP whitelist (uncomment in production)
        # if not security.is_valid_ip(client_ip, FISERV_IP_WHITELIST):
        #     logger.warning(f"S2S notification from unauthorized IP: {client_ip}")
        #     # Still return 200 OK to prevent retries
        #     return Response(content="OK", status_code=200)
        
        # Parse form data
        form_data = await request.form()
        params = dict(form_data)
        
        logger.info(f"S2S notification received for order: {params.get('oid', 'unknown')}")
        logger.debug(f"S2S params: {params}")
        
        # Extract hash from params
        received_hash = params.get('notification_hash') or params.get('response_hash') or params.get('hash')
        
        if not received_hash:
            logger.error("No hash in S2S notification")
            # Still return 200 OK
            return Response(content="OK", status_code=200)
        
        # Verify signature
        if not security.verify_signature(params, received_hash):
            logger.error(f"Invalid signature for order: {params.get('oid')}")
            # Log for security audit but still return 200 OK
            suspicious_notification = {
                'timestamp': datetime.now().isoformat(),
                'ip': client_ip,
                'order_id': params.get('oid'),
                'params': params,
                'reason': 'invalid_signature'
            }
            # In production: save to security log
            logger.warning(f"Suspicious S2S: {suspicious_notification}")
            return Response(content="OK", status_code=200)
        
        # Check for duplicate processing
        order_id = params.get('oid')
        transaction_id = params.get('ipgTransactionId')
        
        if is_duplicate_notification(order_id, transaction_id):
            logger.info(f"Duplicate S2S notification for order: {order_id}")
            return Response(content="OK", status_code=200)
        
        # Process payment status
        status = params.get('status', '').upper()
        approval_code = params.get('approval_code')
        fail_reason = params.get('fail_reason') or params.get('failReason')
        
        # Map Fiserv status to our status
        if status == 'APPROVED':
            payment_status = 'completed'
        elif status == 'DECLINED':
            payment_status = 'failed'
        elif status == 'CANCELLED':
            payment_status = 'cancelled'
        else:
            payment_status = 'pending'
        
        # Update payment record
        payment_update = {
            'status': payment_status,
            'fiserv_transaction_id': transaction_id,
            'fiserv_status': status,
            'approval_code': approval_code,
            'fail_reason': fail_reason,
            'processed_at': datetime.now().isoformat(),
            'last_s2s_notification': params
        }
        
        # Find and update payment by order_id
        payments = load_payments()
        payment_found = False
        
        for i, payment in enumerate(payments):
            if payment.get('order_id') == order_id:
                # Add to S2S notification history
                if 's2s_notifications' not in payment:
                    payment['s2s_notifications'] = []
                
                payment['s2s_notifications'].append({
                    'timestamp': datetime.now().isoformat(),
                    'status': status,
                    'transaction_id': transaction_id,
                    'params': params
                })
                
                # Update payment fields
                payment.update(payment_update)
                payments[i] = payment
                payment_found = True
                break
        
        if payment_found:
            save_payments(payments)
            logger.info(f"Payment {order_id} updated to status: {payment_status}")
            
            # Background task: Send confirmation email if approved
            if payment_status == 'completed':
                background_tasks.add_task(
                    send_payment_confirmation,
                    order_id,
                    params.get('bmail')
                )
        else:
            logger.error(f"Payment not found for order: {order_id}")
        
        # ALWAYS return 200 OK to Fiserv
        return Response(content="OK", status_code=200)
        
    except Exception as e:
        logger.error(f"S2S processing error: {str(e)}", exc_info=True)
        # Even on error, return 200 OK to prevent endless retries
        return Response(content="OK", status_code=200)

@router.get("/{payment_id}/status")
async def get_payment_status(payment_id: str):
    """
    Get payment status
    Note: This shows the status from our database, which is updated by S2S notifications
    """
    payment = get_payment_by_id(payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {
        'payment_id': payment['payment_id'],
        'order_id': payment.get('order_id'),
        'status': payment['status'],
        'amount': payment['amount'],
        'created_at': payment['created_at'],
        'processed_at': payment.get('processed_at'),
        'approval_code': payment.get('approval_code'),
        'transaction_id': payment.get('fiserv_transaction_id')
    }

@router.get("/{payment_id}/verify")
async def verify_payment(payment_id: str):
    """
    Verify payment status for security
    Used by success/failure pages to confirm actual payment status
    """
    payment = get_payment_by_id(payment_id)
    
    if not payment:
        return {'verified': False, 'status': 'not_found'}
    
    # Don't trust URL parameters - check actual status from S2S
    actual_status = payment.get('status', 'pending')
    
    return {
        'verified': True,
        'payment_id': payment_id,
        'order_id': payment.get('order_id'),
        'status': actual_status,
        'is_completed': actual_status == 'completed',
        'is_failed': actual_status in ['failed', 'cancelled'],
        'is_pending': actual_status == 'pending',
        'message': get_status_message(actual_status)
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

async def send_payment_confirmation(order_id: str, email: Optional[str]):
    """
    Background task to send payment confirmation email
    """
    if not email:
        return
    
    try:
        # In production: implement actual email sending
        logger.info(f"Would send confirmation email for order {order_id} to {email}")
        # Example: use SendGrid, AWS SES, etc.
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")

# Health check endpoint for monitoring
@router.get("/health")
async def payment_health():
    """Health check for payment system"""
    return {
        'status': 'healthy',
        'gateway': 'fiserv',
        'mode': os.getenv('ENVIRONMENT', 'production')
    }
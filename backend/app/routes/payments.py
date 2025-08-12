from fastapi import APIRouter, HTTPException, Header, Request
from typing import Dict, Any, Optional
import json
import os
import hmac
import hashlib
from datetime import datetime
import uuid

from ..models import PaymentRequest, Payment, PaymentStatus, WebhookPayload
# from ..utils.fiserv_client import fiserv_client  # Not used currently
from ..utils.fiserv_ipg_client import fiserv_ipg_client
from .organization import load_organization

router = APIRouter(prefix="/api", tags=["payments"])

PAYMENTS_FILE = "app/data/payments.json"

def load_payments() -> list:
    """Load payments from JSON file"""
    try:
        with open(PAYMENTS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_payments(payments: list):
    """Save payments to JSON file"""
    with open(PAYMENTS_FILE, "w") as f:
        json.dump(payments, f, indent=2, default=str)

def update_goal_amount(goal_id: str, amount: float):
    """Update collected amount for a goal"""
    try:
        with open("app/data/organization.json", "r", encoding="utf-8") as f:
            org_data = json.load(f)
        
        for goal in org_data["goals"]:
            if goal["id"] == goal_id:
                goal["collected_amount"] += amount
                break
        
        with open("app/data/organization.json", "w", encoding="utf-8") as f:
            json.dump(org_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error updating goal amount: {e}")

@router.post("/payments/initiate")
async def initiate_payment(payment_request: PaymentRequest) -> Dict[str, Any]:
    """Initiate a payment for a charity goal"""
    # Validate goal exists
    org = load_organization()
    goal = next((g for g in org.goals if g.id == payment_request.goal_id), None)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Create payment record
    payment_id = str(uuid.uuid4())
    payment = Payment(
        id=payment_id,
        goal_id=payment_request.goal_id,
        amount=payment_request.amount,
        payment_method=payment_request.payment_method,
        donor_name=payment_request.donor_name,
        donor_email=payment_request.donor_email,
        message=payment_request.message
    )
    
    # Create payment with Fiserv IPG Connect
    try:
        # URLs for payment flow
        base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:5174")
        # Don't include webhook URL if it's localhost (Fiserv can't reach it)
        webhook_base = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:8001')
        webhook_url = f"{webhook_base}/api/webhooks/fiserv" if 'localhost' not in webhook_base else None
        
        # Success/failure URLs - these will handle the redirect back from Fiserv
        success_url = f"{base_url}/platnosc/{payment.id}/status?result=success"
        failure_url = f"{base_url}/platnosc/{payment.id}/status?result=failure"
        
        # Get customer info if provided
        customer_info = {}
        if payment.donor_name:
            customer_info['name'] = payment.donor_name
        if payment.donor_email:
            customer_info['email'] = payment.donor_email
        
        # Create form data for IPG Connect
        form_data = fiserv_ipg_client.create_payment_form_data(
            amount=payment.amount,
            order_id=payment.id,
            description=f"Darowizna na cel: {goal.name}",
            success_url=success_url,
            failure_url=failure_url,
            notification_url=webhook_url,
            payment_method=payment_request.payment_method.value if payment_request.payment_method else None,
            customer_info=customer_info
        )
        
        # For IPG Connect, we need to return a form that will be submitted by the frontend
        # Store the form data temporarily and provide a URL to submit it
        payment.payment_url = f"{base_url}/platnosc/{payment.id}/metoda?amount={payment.amount}&goal={goal.name}&goalId={payment.goal_id}"
        payment.fiserv_transaction_id = f"IPG-{payment.id[:8]}"
        payment.fiserv_checkout_id = payment.id
        
        # Store form data in payment record for later use
        payment.form_data = form_data
            
    except Exception as e:
        # Fallback to mock payment for development
        frontend_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:5174")
        payment.payment_url = f"{frontend_url}/platnosc/{payment.id}/metoda?amount={payment.amount}&goal={goal.name}&goalId={payment.goal_id}"
        payment.fiserv_transaction_id = f"MOCK-TXN-{payment.id[:8]}"
        payment.fiserv_checkout_id = f"MOCK-CHK-{payment.id[:8]}"
        print(f"Fiserv IPG error (using mock): {str(e)}")
    
    # Save payment
    payments = load_payments()
    payments.append(payment.dict())
    save_payments(payments)
    
    return {
        "payment_id": payment.id,
        "payment_url": payment.payment_url,
        "amount": payment.amount,
        "goal": goal.name
    }

@router.get("/payments/{payment_id}/status")
async def get_payment_status(payment_id: str) -> Dict[str, Any]:
    """Get payment status"""
    payments = load_payments()
    payment = next((p for p in payments if p["id"] == payment_id), None)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {
        "payment_id": payment["id"],
        "status": payment["status"],
        "amount": payment["amount"],
        "updated_at": payment["updated_at"],
        "payment_url": payment.get("payment_url")
    }

@router.get("/payments/{payment_id}/form-data")
async def get_payment_form_data(payment_id: str) -> Dict[str, Any]:
    """Get payment form data for IPG Connect submission"""
    payments = load_payments()
    payment = next((p for p in payments if p["id"] == payment_id), None)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if not payment.get("form_data"):
        raise HTTPException(status_code=404, detail="Form data not found")
    
    return payment["form_data"]

@router.post("/payments/{payment_id}/process-mock")
async def process_mock_payment(payment_id: str, request: Request) -> Dict[str, Any]:
    """Process mock payment - simulates successful payment"""
    body = await request.json()
    payment_method = body.get("payment_method", "unknown")
    
    # Load and update payment
    payments = load_payments()
    payment_found = False
    
    for i, payment in enumerate(payments):
        if payment["id"] == payment_id:
            payments[i]["status"] = PaymentStatus.COMPLETED
            payments[i]["payment_method"] = payment_method
            payments[i]["updated_at"] = str(datetime.utcnow())
            
            # Update goal amount
            update_goal_amount(payment["goal_id"], payment["amount"])
            payment_found = True
            break
    
    if not payment_found:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Save updated payments
    save_payments(payments)
    
    return {
        "status": "success",
        "payment_id": payment_id,
        "payment_method": payment_method
    }

@router.get("/webhooks/fiserv")
async def webhook_health_check():
    """Handle Fiserv webhook health check (GET request)"""
    return {"status": "ok", "message": "Webhook endpoint is active"}

@router.post("/webhooks/fiserv")
async def handle_webhook(
    request: Request,
    signature: Optional[str] = Header(None),
    timestamp: Optional[str] = Header(None)
):
    """Handle Fiserv payment webhook"""
    # Get raw body
    body = await request.body()
    body_str = body.decode("utf-8")
    
    # TODO: Verify signature if provided
    # if signature and os.getenv("FISERV_API_SECRET"):
    #     # Implement signature verification
    #     pass
    
    # Parse webhook data
    try:
        data = json.loads(body_str)
        webhook = WebhookPayload(
            transaction_id=data.get("transactionId", ""),
            order_id=data.get("orderId", ""),
            status=data.get("transactionStatus", ""),
            amount=float(data.get("amount", 0)),
            currency=data.get("currency", "PLN"),
            timestamp=data.get("timestamp", str(datetime.utcnow()))
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {str(e)}")
    
    # Update payment status
    payments = load_payments()
    payment_updated = False
    
    for i, payment in enumerate(payments):
        if payment["id"] == webhook.order_id:
            # Map Fiserv status to our status
            if webhook.status in ["APPROVED", "SUCCESS"]:
                payments[i]["status"] = PaymentStatus.COMPLETED
                # Update goal amount if payment completed
                if payment["status"] != PaymentStatus.COMPLETED:
                    update_goal_amount(payment["goal_id"], payment["amount"])
            elif webhook.status in ["DECLINED", "FAILED"]:
                payments[i]["status"] = PaymentStatus.FAILED
            elif webhook.status == "CANCELLED":
                payments[i]["status"] = PaymentStatus.CANCELLED
            
            payments[i]["updated_at"] = str(datetime.utcnow())
            payment_updated = True
            break
    
    if payment_updated:
        save_payments(payments)
    
    return {"status": "ok"}
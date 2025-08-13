import os
import hmac
import hashlib
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FiservIPGClient:
    """Fiserv IPG Connect client for form-based payment integration"""
    
    def __init__(self):
        # Load credentials from environment
        self.store_id = os.getenv('FISERV_STORE_ID', '760995999')
        self.shared_secret = os.getenv('FISERV_SHARED_SECRET', 'j}2W3P)Lwv')
        self.gateway_url = os.getenv('FISERV_GATEWAY_URL', 'https://test.ipg-online.com/connect/gateway/processing')
        
        # Check for additional environment variables that might be needed
        self.merchant_id = os.getenv('FISERV_MERCHANT_ID', self.store_id)
        self.terminal_id = os.getenv('FISERV_TERMINAL_ID', self.store_id)
        
        logger.info(f"FiservIPGClient initialized with store_id: {self.store_id}")
    
    def create_payment_form_data(self, amount: float, order_id: str, description: str, 
                                success_url: str, failure_url: str, notification_url: Optional[str] = None,
                                payment_method: Optional[str] = None, customer_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Create form data for IPG Connect payment submission"""
        
        # CRITICAL: Get current WARSAW time, NOT UTC!
        # Fiserv expects local Warsaw time for Polish stores
        warsaw_tz = ZoneInfo('Europe/Warsaw')
        now_warsaw = datetime.now(warsaw_tz)
        
        # Format timestamp exactly as Fiserv expects: YYYY:MM:DD-HH:MM:SS
        # This MUST be Warsaw time, not UTC!
        txndatetime = now_warsaw.strftime("%Y:%m:%d-%H:%M:%S")
        
        # Log for debugging
        logger.info(f"Generated Warsaw timestamp: {txndatetime} (timezone: Europe/Warsaw)")
        
        # Build form fields according to IPG Connect specification
        form_fields = {
            'storename': self.store_id,
            'txntype': 'sale',
            'timezone': 'Europe/Warsaw',  # MUST be Europe/Warsaw for Polish stores
            'txndatetime': txndatetime,    # Warsaw time, NOT UTC!
            'hash_algorithm': 'HMACSHA256',
            'chargetotal': f"{amount:.2f}",
            'currency': '985',  # PLN
            'checkoutoption': 'combinedpage',  # Required for response URLs
            'oid': order_id,
            'responseSuccessURL': success_url,
            'responseFailURL': failure_url,
        }
        
        # Add notification URL if provided (and not localhost)
        if notification_url and 'localhost' not in notification_url:
            form_fields['transactionNotificationURL'] = notification_url
            
        # Generate hash ONLY from required fields (before adding optional fields)
        hash_fields = {
            'chargetotal': form_fields['chargetotal'],
            'currency': form_fields['currency'],
            'storename': form_fields['storename'],
            'txndatetime': form_fields['txndatetime']
        }
        hash_value = self._generate_hash(hash_fields)
        form_fields['hashExtended'] = hash_value  # Use hashExtended as per IPG Connect docs
        
        # Add customer info AFTER hash generation (these are NOT included in hash)
        if customer_info:
            if customer_info.get('name'):
                form_fields['bname'] = customer_info['name']
            if customer_info.get('email'):
                form_fields['bmail'] = customer_info['email']  # Changed from 'bemail' to 'bmail'
                
        # Add payment method specific fields
        if payment_method == 'blik':
            form_fields['blikPayment'] = 'true'
        
        logger.debug(f"Generated form data for payment {order_id}, hash: {hash_value[:20]}...")
        
        return {
            'form_action': self.gateway_url,
            'form_fields': form_fields
        }
    
    def _sanitize_text(self, text: str) -> str:
        """Remove Polish diacritical marks and special characters"""
        replacements = {
            'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 
            'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
            'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
            'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
        }
        for polish, ascii_char in replacements.items():
            text = text.replace(polish, ascii_char)
        return text
    
    def _generate_hash(self, params: Dict[str, str]) -> str:
        """Generate HMAC-SHA256 hash for IPG Connect"""
        # Fields to exclude from hash calculation
        exclude_fields = {'hash', 'hashExtended', 'hash_algorithm'}
        
        # Sort parameters alphabetically and filter out excluded fields
        sorted_params = sorted([
            (k, v) for k, v in params.items() 
            if k not in exclude_fields and v
        ])
        
        # Join ONLY VALUES with pipe separator (as per guide)
        values_to_hash = '|'.join(str(v) for k, v in sorted_params)
        
        logger.debug(f"Hash input string: {values_to_hash[:100]}...")
        logger.debug(f"Full hash string: {values_to_hash}")
        
        # Calculate HMAC-SHA256
        hash_value = hmac.new(
            self.shared_secret.encode('utf-8'),
            values_to_hash.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Return Base64 encoded hash
        return base64.b64encode(hash_value).decode('utf-8')

# Create singleton instance
fiserv_ipg_client = FiservIPGClient()

# Keep the standalone function for backward compatibility
def create_payment_form_data(amount, order_id, description, success_url, failure_url, 
                           notification_url=None, payment_method=None, customer_info=None):
    """Legacy function wrapper for backward compatibility"""
    return fiserv_ipg_client.create_payment_form_data(
        amount=amount,
        order_id=order_id,
        description=description,
        success_url=success_url,
        failure_url=failure_url,
        notification_url=notification_url,
        payment_method=payment_method,
        customer_info=customer_info
    )
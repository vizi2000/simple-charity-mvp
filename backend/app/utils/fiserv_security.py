"""
Fiserv Payment Gateway Security Module
Full implementation based on IMPLEMENTATION_GUIDE.md
"""

import hashlib
import hmac
import base64
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class FiservSecurity:
    """Handles all security aspects of Fiserv integration"""
    
    def __init__(self, shared_secret: str, store_id: str):
        self.shared_secret = shared_secret
        self.store_id = store_id
        self.warsaw_tz = pytz.timezone('Europe/Warsaw')
    
    def generate_hash(self, params: Dict[str, str]) -> str:
        """
        Generate HMAC-SHA256 hash for Fiserv payment
        
        Args:
            params: Dictionary of payment parameters
            
        Returns:
            Base64 encoded hash string
        """
        # Sort parameters alphabetically by key
        sorted_keys = sorted(params.keys())
        
        # Create string to sign by joining values with pipe separator
        values = [str(params[key]) for key in sorted_keys]
        string_to_sign = '|'.join(values)
        
        logger.debug(f"String to sign: {string_to_sign}")
        
        # Generate HMAC-SHA256
        signature = hmac.new(
            self.shared_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Encode in Base64
        hash_value = base64.b64encode(signature).decode('utf-8')
        
        logger.debug(f"Generated hash: {hash_value}")
        
        return hash_value
    
    def verify_signature(self, params: Dict[str, str], received_hash: str) -> bool:
        """
        Verify S2S notification signature from Fiserv
        
        Args:
            params: Received parameters from Fiserv
            received_hash: Hash received from Fiserv
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Remove hash fields from parameters
        params_to_verify = {
            k: v for k, v in params.items() 
            if k not in ['hash', 'hashExtended', 'response_hash', 'notification_hash']
        }
        
        # Generate hash for comparison
        calculated_hash = self.generate_hash(params_to_verify)
        
        # Constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(calculated_hash, received_hash)
        
        if not is_valid:
            logger.warning(f"Invalid signature for order: {params.get('oid', 'unknown')}")
            logger.debug(f"Expected: {calculated_hash}, Received: {received_hash}")
        
        return is_valid
    
    def validate_payment_data(self, data: Dict) -> List[str]:
        """
        Validate payment data before processing
        
        Args:
            data: Payment data to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate amount
        if 'amount' not in data or not data['amount']:
            errors.append('Amount is required')
        else:
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    errors.append('Amount must be greater than 0')
                # Check for 2 decimal places
                amount_str = f"{amount:.2f}"
                if str(data['amount']) != amount_str and str(data['amount']) != str(int(amount)):
                    errors.append('Amount must have at most 2 decimal places')
            except (ValueError, TypeError):
                errors.append('Invalid amount format')
        
        # Validate order ID format
        if 'order_id' in data:
            import re
            if not re.match(r'^[A-Za-z0-9\-_]+$', str(data['order_id'])):
                errors.append('Invalid order ID format')
        
        # Validate email if provided
        if 'email' in data and data['email']:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors.append('Invalid email format')
        
        return errors
    
    def get_transaction_datetime(self) -> str:
        """
        Get current datetime in Warsaw timezone in Fiserv format
        
        Returns:
            Formatted datetime string (YYYY:MM:DD-HH:mm:ss)
        """
        now = datetime.now(self.warsaw_tz)
        return now.strftime('%Y:%m:%d-%H:%M:%S')
    
    def prepare_payment_form_data(self, 
                                  amount: float,
                                  order_id: str,
                                  success_url: str,
                                  fail_url: str,
                                  notification_url: str,
                                  currency: str = '985',  # PLN
                                  payment_method: str = 'M',
                                  customer_data: Optional[Dict] = None) -> Dict[str, str]:
        """
        Prepare complete form data for Fiserv payment
        
        Args:
            amount: Payment amount
            order_id: Unique order identifier
            success_url: URL for successful payment redirect
            fail_url: URL for failed payment redirect
            notification_url: S2S notification URL (must be HTTPS in production)
            currency: Currency code (985 for PLN)
            payment_method: Payment method (M for mixed)
            customer_data: Optional customer information
            
        Returns:
            Dictionary with all form fields including hash
        """
        # Format amount with 2 decimal places
        amount_str = f"{float(amount):.2f}"
        
        # Get transaction datetime
        txn_datetime = self.get_transaction_datetime()
        
        # Build parameters dictionary
        params = {
            'chargetotal': amount_str,
            'checkoutoption': 'combinedpage',
            'currency': currency,
            'hash_algorithm': 'HMACSHA256',
            'oid': order_id,
            'paymentMethod': payment_method,
            'responseFailURL': fail_url,
            'responseSuccessURL': success_url,
            'storename': self.store_id,
            'timezone': 'Europe/Warsaw',
            'transactionNotificationURL': notification_url,
            'txndatetime': txn_datetime,
            'txntype': 'sale'
        }
        
        # Add customer data if provided
        if customer_data:
            if 'email' in customer_data:
                params['bmail'] = customer_data['email']
            if 'name' in customer_data:
                params['bname'] = customer_data['name']
            if 'address' in customer_data:
                params['baddr1'] = customer_data['address']
            if 'city' in customer_data:
                params['bcity'] = customer_data['city']
            if 'postal_code' in customer_data:
                params['bzip'] = customer_data['postal_code']
            if 'country' in customer_data:
                params['bcountry'] = customer_data['country']
        
        # Generate hash
        hash_value = self.generate_hash(params)
        
        # Add hash to form data
        params['hashExtended'] = hash_value
        
        return params
    
    def is_valid_ip(self, ip_address: str, whitelist: List[str]) -> bool:
        """
        Check if IP address is in whitelist (for S2S notifications)
        
        Args:
            ip_address: IP to check
            whitelist: List of allowed IPs or CIDR ranges
            
        Returns:
            True if IP is allowed, False otherwise
        """
        import ipaddress
        
        try:
            ip = ipaddress.ip_address(ip_address)
            
            for allowed in whitelist:
                try:
                    # Check if it's a network range
                    if '/' in allowed:
                        network = ipaddress.ip_network(allowed, strict=False)
                        if ip in network:
                            return True
                    # Check exact match
                    elif str(ip) == allowed:
                        return True
                except ValueError:
                    logger.error(f"Invalid IP/network in whitelist: {allowed}")
                    continue
                    
        except ValueError:
            logger.error(f"Invalid IP address: {ip_address}")
            
        return False

# Fiserv IP ranges for production (verify with current documentation)
FISERV_IP_WHITELIST = [
    '185.60.40.0/24',  # Example Fiserv range - VERIFY WITH DOCUMENTATION
    '195.35.90.0/24',  # Example Fiserv range - VERIFY WITH DOCUMENTATION
    # Add actual Fiserv IP ranges from documentation
]

def create_security_handler(config: Dict) -> FiservSecurity:
    """
    Factory function to create FiservSecurity instance
    
    Args:
        config: Configuration dictionary with shared_secret and store_id
        
    Returns:
        FiservSecurity instance
    """
    return FiservSecurity(
        shared_secret=config['shared_secret'],
        store_id=config['store_id']
    )
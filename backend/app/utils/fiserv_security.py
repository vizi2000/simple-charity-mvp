"""
Fiserv Payment Gateway Security Module
Full implementation based on IMPLEMENTATION_GUIDE.md
"""

import hashlib
import hmac
import base64
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Optional, List
from datetime import datetime
import pytz

# Wczytaj zmienne środowiskowe
load_dotenv()

# Pobierz sekret z zmiennych środowiskowych dla bezpieczeństwa
FISERV_SHARED_SECRET = os.getenv("FISERV_SHARED_SECRET", "j}2W3P)Lwv")

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

def create_hash(params: dict) -> str:
    """
    Generuje bezpieczny hash HMAC-SHA256 na podstawie wszystkich parametrów żądania,
    używając separatora '|' i zwracając w formacie Base64.
    
    Args:
        params (dict): Słownik zawierający wszystkie parametry wysyłane do Fiserv.

    Returns:
        str: Base64 encoded hash string.
    """
    # 1. Usuń pola hash jeśli istnieją
    params_to_hash = {k: v for k, v in params.items() 
                      if k not in ['hash', 'hashExtended', 'response_hash', 'notification_hash']}
    
    # 2. Posortuj parametry alfabetycznie według kluczy
    sorted_keys = sorted(params_to_hash.keys())
    
    # 3. Stwórz ciąg danych, łącząc wartości w posortowanej kolejności za pomocą separatora '|'
    data_string = "|".join(str(params_to_hash[key]) for key in sorted_keys)
    
    logger.debug(f"Hash calculation - Keys: {sorted_keys}")
    logger.debug(f"Hash calculation - Data: {data_string[:100]}...")
    
    # 4. Oblicz hash HMAC-SHA256 używając sharedSecret jako klucza
    secret_bytes = FISERV_SHARED_SECRET.encode('utf-8')
    data_bytes = data_string.encode('utf-8')
    
    hashed = hmac.new(secret_bytes, data_bytes, hashlib.sha256)
    
    # 5. Zwróć hash w formacie Base64 (NIE hex!)
    base64_hash = base64.b64encode(hashed.digest()).decode('utf-8')
    
    logger.debug(f"Generated Base64 hash: {base64_hash}")
    
    return base64_hash

def verify_notification_hash(notification_data: dict) -> bool:
    """
    Weryfikuje hash otrzymany w powiadomieniu S2S od Fiserv.
    
    Args:
        notification_data (dict): Dane otrzymane w powiadomieniu.

    Returns:
        bool: True, jeśli hash jest poprawny, w przeciwnym razie False.
    """
    # Znajdź pole z hashem
    received_hash = None
    if "response_hash" in notification_data:
        received_hash = notification_data["response_hash"]
    elif "notification_hash" in notification_data:
        received_hash = notification_data["notification_hash"]
    elif "hashExtended" in notification_data:
        received_hash = notification_data["hashExtended"]
    
    if not received_hash:
        return False
    
    # Metoda 1: Weryfikacja wszystkich pól
    params_copy = dict(notification_data)
    for hash_field in ['response_hash', 'notification_hash', 'hash', 'hashExtended']:
        params_copy.pop(hash_field, None)
    
    # Spróbuj z Base64
    calculated_hash = create_hash(params_copy)
    if hmac.compare_digest(calculated_hash, received_hash):
        return True
    
    # Metoda 2: Weryfikacja legacy (4 pola bez separatora)
    if all(k in notification_data for k in ["approval_code", "chargetotal", "currency", "txndatetime"]):
        fields_for_hash = [
            notification_data.get("approval_code", ""),
            notification_data.get("chargetotal", ""),
            notification_data.get("currency", ""),
            notification_data.get("txndatetime", "")
        ]
        
        data_string = "".join(str(field) for field in fields_for_hash)
        
        secret_bytes = FISERV_SHARED_SECRET.encode('utf-8')
        data_bytes = data_string.encode('utf-8')
        
        calculated_hash_obj = hmac.new(secret_bytes, data_bytes, hashlib.sha256)
        # Spróbuj hex dla legacy
        calculated_hash_hex = calculated_hash_obj.hexdigest()
        
        if hmac.compare_digest(calculated_hash_hex, received_hash):
            return True
    
    return False

def create_security_handler(config: Dict) -> FiservSecurity:
    """
    Factory function to create FiservSecurity instance
    
    Args:
        config: Configuration dictionary with shared_secret and store_id
        
    Returns:
        FiservSecurity instance
    """
    return FiservSecurity(
        shared_secret=config.get('shared_secret', FISERV_SHARED_SECRET),
        store_id=config['store_id']
    )
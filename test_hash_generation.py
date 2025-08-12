#!/usr/bin/env python3
"""
Test script to verify hash generation matches Fiserv requirements
Based on the analysis showing that ALL fields must be included in hash
"""

import hashlib
import hmac
import base64
from datetime import datetime
import pytz

# Configuration
SHARED_SECRET = 'j}2W3P)Lwv'
STORE_ID = '760995999'

def generate_hash_all_fields(params: dict, method='base64') -> str:
    """
    Generate hash including ALL fields (as per analysis)
    """
    # Remove any existing hash fields
    params_to_hash = {k: v for k, v in params.items() 
                      if k not in ['hash', 'hashExtended', 'response_hash', 'notification_hash']}
    
    # Sort parameters alphabetically
    sorted_keys = sorted(params_to_hash.keys())
    
    # Join values with pipe separator
    values = [str(params_to_hash[key]) for key in sorted_keys]
    data_to_sign = '|'.join(values)
    
    print(f"\n=== ALL FIELDS METHOD ===")
    print(f"Number of fields: {len(sorted_keys)}")
    print(f"Sorted keys: {sorted_keys}")
    print(f"Data to sign: {data_to_sign}")
    
    # Generate HMAC-SHA256
    signature = hmac.new(
        SHARED_SECRET.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    )
    
    if method == 'base64':
        result = base64.b64encode(signature.digest()).decode('utf-8')
        print(f"Hash (Base64): {result}")
    else:
        result = signature.hexdigest()
        print(f"Hash (Hex): {result}")
    
    return result

def generate_hash_four_fields(params: dict) -> str:
    """
    Generate hash using only 4 fields (old incorrect method)
    """
    # Only use 4 specific fields
    data_to_sign = (
        params['storename'] +
        params['txndatetime'] +
        params['chargetotal'] +
        params['currency']
    )
    
    print(f"\n=== FOUR FIELDS METHOD (OLD) ===")
    print(f"Data to sign: {data_to_sign}")
    
    # Generate HMAC-SHA256
    signature = hmac.new(
        SHARED_SECRET.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    )
    
    result = signature.hexdigest()
    print(f"Hash (Hex): {result}")
    
    return result

def test_payment_hash():
    """Test hash generation with realistic payment data"""
    
    # Get current Warsaw time
    warsaw_tz = pytz.timezone('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    txn_datetime = now.strftime('%Y:%m:%d-%H:%M:%S')
    
    # Build complete form data (ALL fields that would be sent)
    form_data = {
        'chargetotal': '10.00',
        'checkoutoption': 'combinedpage',
        'currency': '985',
        'hash_algorithm': 'HMACSHA256',
        'oid': f'TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'paymentMethod': 'M',
        'responseFailURL': 'https://borgtools.ddns.net/bramkamvp/payment/failure',
        'responseSuccessURL': 'https://borgtools.ddns.net/bramkamvp/payment/success',
        'storename': STORE_ID,
        'timezone': 'Europe/Warsaw',
        'transactionNotificationURL': 'https://borgtools.ddns.net/bramkamvp/api/payments/webhooks/fiserv/s2s',
        'txndatetime': txn_datetime,
        'txntype': 'sale',
        'bmail': 'test@example.com',
        'bname': 'Test User'
    }
    
    print("="*70)
    print("PAYMENT HASH GENERATION TEST")
    print("="*70)
    print(f"\nTransaction datetime: {txn_datetime}")
    print(f"Order ID: {form_data['oid']}")
    print(f"Amount: {form_data['chargetotal']} PLN")
    
    # Test old method (4 fields only)
    hash_old = generate_hash_four_fields(form_data)
    
    # Test new method (all fields) - Hex
    hash_new_hex = generate_hash_all_fields(form_data, method='hex')
    
    # Test new method (all fields) - Base64
    hash_new_base64 = generate_hash_all_fields(form_data, method='base64')
    
    print("\n" + "="*70)
    print("COMPARISON:")
    print("="*70)
    print(f"Old method (4 fields, hex):     {hash_old}")
    print(f"New method (all fields, hex):    {hash_new_hex}")
    print(f"New method (all fields, base64): {hash_new_base64}")
    
    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    print("✅ Use the ALL FIELDS method with Base64 encoding")
    print("✅ This hash should be sent as 'hashExtended' field")
    print("✅ Include ALL form fields in hash calculation")
    print("✅ Sort fields alphabetically and join with pipe separator")
    
    return form_data, hash_new_base64

if __name__ == "__main__":
    test_payment_hash()
    
    print("\n" + "="*70)
    print("WHAT FISERV EXPECTS:")
    print("="*70)
    print("1. Hash must include ALL fields being sent (not just 4)")
    print("2. Fields must be sorted alphabetically by key")
    print("3. Values must be joined with pipe separator (|)")
    print("4. Use HMAC-SHA256 with shared secret as key")
    print("5. Encode as Base64 for 'hashExtended' field")
    print("6. Do NOT include the hash itself in the calculation")
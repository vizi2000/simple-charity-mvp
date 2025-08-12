#!/usr/bin/env python3
"""
Verify hash generation for specific payment
"""

import hashlib
import hmac

def verify_hash(storename, txndatetime, chargetotal, currency, shared_secret, expected_hash):
    """Verify HMAC-SHA256 hash"""
    # Create data to sign (WITHOUT sharedSecret!)
    data_to_sign = f"{storename}{txndatetime}{chargetotal}{currency}"
    
    print(f"Data to sign: {data_to_sign}")
    print(f"HMAC Key: {shared_secret}")
    
    # Generate HMAC-SHA256
    hash_obj = hmac.new(
        shared_secret.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    )
    
    calculated_hash = hash_obj.hexdigest()
    
    print(f"Calculated hash: {calculated_hash}")
    print(f"Expected hash:   {expected_hash}")
    
    if calculated_hash == expected_hash:
        print("✅ HASH VERIFICATION SUCCESSFUL!")
        return True
    else:
        print("❌ HASH VERIFICATION FAILED!")
        return False

# Test with actual payment data from API response
print("="*60)
print("HASH VERIFICATION TEST")
print("="*60)

# Test case 1: Small amount (1.00 PLN)
print("\nTest 1: Small amount (1.00 PLN)")
verify_hash(
    storename="760995999",
    txndatetime="2025:08:12-02:35:46",
    chargetotal="1.00",
    currency="985",
    shared_secret="j}2W3P)Lwv",
    expected_hash="7bd75af7ccaf4c63f178912d51a901e4828042a75320884c2717789b27bc3ef0"
)

# Test case 2: Regular amount (25.50 PLN)
print("\nTest 2: Regular amount (25.50 PLN)")
verify_hash(
    storename="760995999",
    txndatetime="2025:08:12-02:35:47",
    chargetotal="25.50",
    currency="985",
    shared_secret="j}2W3P)Lwv",
    expected_hash="e8d925318a7111c5d350b60e9c30fe0d94b7da72d0f57032c96eadce50bd0870"
)

# Test case 3: Large amount (999.99 PLN)
print("\nTest 3: Large amount (999.99 PLN)")
verify_hash(
    storename="760995999",
    txndatetime="2025:08:12-02:35:48",
    chargetotal="999.99",
    currency="985",
    shared_secret="j}2W3P)Lwv",
    expected_hash="77df6176e65841d217c82dd91471fdda01bc39164563fc362b83bcf9ec6ae607"
)

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
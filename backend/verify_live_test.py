#!/usr/bin/env python3
"""
Verify the live test hash
"""

import hashlib
import hmac

def verify_live_hash():
    """Verify HMAC-SHA256 hash for live test"""
    # Data from API response
    storename = "760995999"
    txndatetime = "2025:08:12-02:43:35"
    chargetotal = "50.00"
    currency = "985"
    shared_secret = "j}2W3P)Lwv"
    expected_hash = "fdd97624720f720a4ad1254be8b0132d33678c8846c54a53d003772789d3fee7"
    
    print("="*60)
    print("LIVE API TEST HASH VERIFICATION")
    print("="*60)
    
    # Create data to sign
    data_to_sign = f"{storename}{txndatetime}{chargetotal}{currency}"
    
    print(f"Store:      {storename}")
    print(f"DateTime:   {txndatetime}")
    print(f"Amount:     {chargetotal}")
    print(f"Currency:   {currency}")
    print(f"Data string: {data_to_sign}")
    print(f"HMAC Key:   {shared_secret}")
    
    # Generate HMAC-SHA256
    hash_obj = hmac.new(
        shared_secret.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    )
    
    calculated_hash = hash_obj.hexdigest()
    
    print(f"\nExpected hash:   {expected_hash}")
    print(f"Calculated hash: {calculated_hash}")
    
    if calculated_hash == expected_hash:
        print("\n✅ LIVE API HASH IS CORRECT!")
        print("The backend is generating proper HMAC-SHA256 hashes!")
        return True
    else:
        print("\n❌ LIVE API HASH MISMATCH!")
        return False

if __name__ == "__main__":
    verify_live_hash()
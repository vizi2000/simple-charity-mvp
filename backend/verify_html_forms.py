#!/usr/bin/env python3
"""
Verify hashes from generated HTML test forms
"""

import hashlib
import hmac

def verify_form_hash(form_name, storename, txndatetime, chargetotal, currency, shared_secret, expected_hash):
    """Verify HMAC-SHA256 hash for HTML form"""
    print(f"\nVerifying {form_name}:")
    print(f"  Store: {storename}")
    print(f"  DateTime: {txndatetime}")
    print(f"  Amount: {chargetotal} PLN")
    print(f"  Currency: {currency}")
    
    # Create data to sign
    data_to_sign = f"{storename}{txndatetime}{chargetotal}{currency}"
    print(f"  Data to sign: {data_to_sign}")
    
    # Generate HMAC-SHA256
    hash_obj = hmac.new(
        shared_secret.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    )
    
    calculated_hash = hash_obj.hexdigest()
    
    print(f"  Expected:   {expected_hash}")
    print(f"  Calculated: {calculated_hash}")
    
    if calculated_hash == expected_hash:
        print(f"  ✅ HASH CORRECT!")
        return True
    else:
        print(f"  ❌ HASH MISMATCH!")
        return False

print("="*60)
print("HTML FORMS HASH VERIFICATION")
print("="*60)

shared_secret = "j}2W3P)Lwv"
results = []

# Form 1: 10 PLN
results.append(verify_form_hash(
    "10 PLN Form",
    storename="760995999",
    txndatetime="2025:08:12-02:35:52",
    chargetotal="10.00",
    currency="985",
    shared_secret=shared_secret,
    expected_hash="f9550a47fbc74d012227fefd572ee40202135ddec771ac61795fba7ec387a712"
))

# Form 2: 25 PLN
results.append(verify_form_hash(
    "25 PLN Form",
    storename="760995999",
    txndatetime="2025:08:12-02:35:52",
    chargetotal="25.00",
    currency="985",
    shared_secret=shared_secret,
    expected_hash="d91858eb6786ab06a867b56606663827612604d4bce208651b643e5762a43411"
))

# Form 3: 100 PLN
results.append(verify_form_hash(
    "100 PLN Form",
    storename="760995999",
    txndatetime="2025:08:12-02:35:52",
    chargetotal="100.00",
    currency="985",
    shared_secret=shared_secret,
    expected_hash="34de45b6c1ce5dd869edc8f88d4e272c88c0d6b9f65a83accf253277e7afa57a"
))

print("\n" + "="*60)
print("SUMMARY:")
print(f"✅ Passed: {sum(results)}/{len(results)}")
print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")

if all(results):
    print("\n🎉 ALL HTML FORM HASHES ARE CORRECT!")
else:
    print("\n⚠️ Some form hashes are incorrect!")

print("="*60)
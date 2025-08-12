#!/usr/bin/env python3
"""
Test exact hash generation as sent to Fiserv
"""
import hashlib
import hmac

# Exact data from the test
storename = "760995999"
txndatetime = "2025:08:12-08:50:14"
chargetotal = "10.00"
currency = "985"
shared_secret = "j}2W3P)Lwv"

print("="*60)
print("TESTING EXACT HASH GENERATION")
print("="*60)

# Method 1: HMAC-SHA256 (what we're using)
data_to_sign = f"{storename}{txndatetime}{chargetotal}{currency}"
print(f"Data to sign: {data_to_sign}")
print(f"Length: {len(data_to_sign)} characters")

hash_obj = hmac.new(
    shared_secret.encode('utf-8'),
    data_to_sign.encode('utf-8'),
    hashlib.sha256
)
hash_value = hash_obj.hexdigest()
print(f"\nHMAC-SHA256 hash: {hash_value}")

# Method 2: Plain SHA256 (wrong, but let's check)
data_with_secret = f"{storename}{txndatetime}{chargetotal}{currency}{shared_secret}"
plain_hash = hashlib.sha256(data_with_secret.encode('utf-8')).hexdigest()
print(f"Plain SHA256 hash: {plain_hash}")

print("\n" + "="*60)
print("FIELDS CHECK:")
print("="*60)
print(f"storename: '{storename}' (should be exactly '760995999')")
print(f"txndatetime: '{txndatetime}' (format: YYYY:MM:DD-HH:MM:SS)")
print(f"chargetotal: '{chargetotal}' (with 2 decimal places)")
print(f"currency: '{currency}' (PLN code)")
print(f"shared_secret: '{shared_secret}' (used as HMAC key)")

# Check if any field has extra spaces
print("\n" + "="*60)
print("CHECKING FOR HIDDEN CHARACTERS:")
print("="*60)
for name, value in [("storename", storename), ("chargetotal", chargetotal), ("currency", currency)]:
    print(f"{name}: repr={repr(value)}, bytes={value.encode('utf-8').hex()}")
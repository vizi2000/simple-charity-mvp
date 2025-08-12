#!/usr/bin/env python3
"""
Test if hash should be Base64 encoded
"""
import hashlib
import hmac
import base64

# Test data
storename = "760995999"
txndatetime = "2025:08:12-08:50:14"
chargetotal = "10.00"
currency = "985"
shared_secret = "j}2W3P)Lwv"

print("="*60)
print("TESTING DIFFERENT HASH ENCODINGS")
print("="*60)

data = f"{storename}{txndatetime}{chargetotal}{currency}"
print(f"Data to sign: {data}")
print()

# HMAC-SHA256 
hash_obj = hmac.new(
    shared_secret.encode('utf-8'),
    data.encode('utf-8'),
    hashlib.sha256
)

# Different encodings
hex_hash = hash_obj.hexdigest()
print(f"Hex (lowercase):  {hex_hash}")

hex_hash_upper = hash_obj.hexdigest().upper()
print(f"Hex (UPPERCASE):  {hex_hash_upper}")

base64_hash = base64.b64encode(hash_obj.digest()).decode('utf-8')
print(f"Base64:           {base64_hash}")

base64_url_safe = base64.urlsafe_b64encode(hash_obj.digest()).decode('utf-8')
print(f"Base64 URL-safe:  {base64_url_safe}")

print("\n" + "="*60)
print("CHECKING WHAT WE'RE SENDING:")
print("="*60)
print(f"We are sending: {hex_hash}")
print(f"Length: {len(hex_hash)} characters")
print(f"Type: Hexadecimal (lowercase)")
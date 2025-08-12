#!/usr/bin/env python3
"""
Test the FIXED hash generation with ALL fields
"""
import hashlib
import hmac

# Sample form data (ALL fields except hash)
form_data = {
    'txntype': 'sale',
    'timezone': 'Europe/Warsaw',
    'txndatetime': '2025:08:12-09:00:00',
    'hash_algorithm': 'HMACSHA256',
    'storename': '760995999',
    'chargetotal': '10.00',
    'currency': '985',
    'checkoutoption': 'combinedpage',
    'oid': 'ORD-20250812-test1234',
    'responseSuccessURL': 'https://borgtools.ddns.net/bramkamvp/payment/success',
    'responseFailURL': 'https://borgtools.ddns.net/bramkamvp/payment/failure',
    'transactionNotificationURL': 'https://borgtools.ddns.net/bramkamvp/api/payments/webhooks/fiserv/s2s',
    'bmail': 'test@example.com',
    'bname': 'Test User'
}

shared_secret = 'j}2W3P)Lwv'

print("="*70)
print("CORRECT HASH GENERATION - INCLUDING ALL FIELDS")
print("="*70)

# Sort fields alphabetically
sorted_keys = sorted(form_data.keys())
print("\nFields in alphabetical order:")
for i, key in enumerate(sorted_keys, 1):
    print(f"  {i:2}. {key:30} = {form_data[key]}")

# Join values with pipe separator
values = [str(form_data[key]) for key in sorted_keys]
data_to_sign = '|'.join(values)

print(f"\nData to sign (with | separator):")
print(f"{data_to_sign}")
print(f"\nLength: {len(data_to_sign)} characters")

# Generate HMAC-SHA256
hash_obj = hmac.new(
    shared_secret.encode('utf-8'),
    data_to_sign.encode('utf-8'),
    hashlib.sha256
)
hash_value = hash_obj.hexdigest()

print(f"\nGenerated hash:")
print(f"{hash_value}")

print("\n" + "="*70)
print("COMPARISON WITH OLD METHOD (WRONG):")
print("="*70)

# Old method - only 4 fields
old_data = f"{form_data['storename']}{form_data['txndatetime']}{form_data['chargetotal']}{form_data['currency']}"
old_hash = hmac.new(
    shared_secret.encode('utf-8'),
    old_data.encode('utf-8'),
    hashlib.sha256
).hexdigest()

print(f"Old data (only 4 fields): {old_data}")
print(f"Old hash: {old_hash}")
print(f"\nHashes match? {hash_value == old_hash}")

if hash_value != old_hash:
    print("✅ CORRECT! Hashes are different because we now include ALL fields")
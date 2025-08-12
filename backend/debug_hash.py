#!/usr/bin/env python3
"""Debug hash generation for Fiserv"""

import json

# Sample form data
form_fields = {
    "storename": "760995999",
    "txntype": "sale",
    "timezone": "Europe/Warsaw",
    "txndatetime": "2025:07:28-19:22:33",
    "chargetotal": "25.00",
    "currency": "985",
    "oid": "3516c694-b09b-46d2-ac07-eaae3d169d5b",
    "comments": "Darowizna na cel: Ofiara na kościół",
    "responseSuccessURL": "http://localhost:5174/platnosc/3516c694-b09b-46d2-ac07-eaae3d169d5b/status?result=success",
    "responseFailURL": "http://localhost:5174/platnosc/3516c694-b09b-46d2-ac07-eaae3d169d5b/status?result=failure",
    "transactionNotificationURL": "http://localhost:8001/api/webhooks/fiserv",
    "language": "pl_PL",
    "authenticateTransaction": "true",
    "bname": "Test User Fixed",
    "bemail": "fixed@test.com",
    "hash_algorithm": "HMACSHA256"
}

# Exclude hash fields
exclude_fields = ['hash', 'hashExtended', 'hash_algorithm']

# Sort parameters alphabetically and filter
sorted_params = sorted([
    (k, v) for k, v in form_fields.items() 
    if k not in exclude_fields and v
])

print("Fields in alphabetical order:")
for k, v in sorted_params:
    print(f"  {k}: {v}")

# Join values with pipe
values_to_hash = '|'.join(str(v) for k, v in sorted_params)

print(f"\nString to hash (length: {len(values_to_hash)}):")
print(values_to_hash)

# Also show first few fields joined
print("\nFirst few fields joined:")
first_few = '|'.join(str(v) for k, v in sorted_params[:5])
print(f"{first_few}...")

# Calculate hash
import hmac
import hashlib
import base64

shared_secret = "j}2W3P)Lwv"
hash_value = hmac.new(
    shared_secret.encode('utf-8'),
    values_to_hash.encode('utf-8'),
    hashlib.sha256
).digest()

hash_base64 = base64.b64encode(hash_value).decode('utf-8')
print(f"\nCalculated hash: {hash_base64}")
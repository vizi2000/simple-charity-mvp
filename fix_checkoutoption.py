#!/usr/bin/env python3
"""
Fix missing checkoutoption field in Fiserv form
"""

import sys

# Read the current file
with open('/var/www/simplepaymentgate/backend/app/routes/payments_working.py', 'r') as f:
    content = f.read()

# Find the form_data section
old_form = """        # Build form data
        form_data = {
            'txntype': 'sale',
            'timezone': 'Europe/Warsaw',
            'txndatetime': txn_datetime,
            'hash_algorithm': 'HMACSHA256',  # Correct algorithm
            'hash': hash_value,  # HMAC-SHA256 hash
            'storename': store_id,
            'chargetotal': amount_str,
            'currency': currency,
            'oid': order_id,"""

new_form = """        # Build form data
        form_data = {
            'txntype': 'sale',
            'timezone': 'Europe/Warsaw',
            'txndatetime': txn_datetime,
            'hash_algorithm': 'HMACSHA256',  # Correct algorithm
            'hash': hash_value,  # HMAC-SHA256 hash
            'storename': store_id,
            'chargetotal': amount_str,
            'currency': currency,
            'checkoutoption': 'combinedpage',  # REQUIRED for combined payment page
            'oid': order_id,"""

if old_form in content:
    content = content.replace(old_form, new_form)
    print("✅ Added checkoutoption field")
else:
    print("❌ Could not find form_data section to update")
    sys.exit(1)

# Write the updated file
with open('/var/www/simplepaymentgate/backend/app/routes/payments_working.py', 'w') as f:
    f.write(content)

print("✅ File updated successfully")
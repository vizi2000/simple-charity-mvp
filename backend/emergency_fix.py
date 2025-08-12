#!/usr/bin/env python3
"""
Emergency fix - Add checkoutoption to payments
"""

import sys
import os

# Read the file
file_path = '/var/www/simplepaymentgate/backend/app/routes/payments_working.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

# Find and fix the form_data section
fixed_lines = []
for i, line in enumerate(lines):
    fixed_lines.append(line)
    # Add checkoutoption after currency line
    if "'currency': currency," in line and i+1 < len(lines):
        # Check if next line already has checkoutoption
        if 'checkoutoption' not in lines[i+1]:
            fixed_lines.append("            'checkoutoption': 'combinedpage',  # CRITICAL: Required field\n")
            print(f"✅ Added checkoutoption at line {i+2}")

# Write back
with open(file_path, 'w') as f:
    f.writelines(fixed_lines)

print("✅ File updated successfully")
print("🔄 Now restart the backend service")
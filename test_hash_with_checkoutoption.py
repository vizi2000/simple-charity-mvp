#!/usr/bin/env python3
"""
Test if checkoutoption should be in hash
"""
import hashlib
import hmac

# Test data
storename = "760995999"
txndatetime = "2025:08:12-08:50:14"
chargetotal = "10.00"
currency = "985"
checkoutoption = "combinedpage"
shared_secret = "j}2W3P)Lwv"

print("="*60)
print("TESTING HASH WITH DIFFERENT COMBINATIONS")
print("="*60)

# Version 1: WITHOUT checkoutoption (current)
data1 = f"{storename}{txndatetime}{chargetotal}{currency}"
hash1 = hmac.new(
    shared_secret.encode('utf-8'),
    data1.encode('utf-8'),
    hashlib.sha256
).hexdigest()
print(f"WITHOUT checkoutoption:")
print(f"  Data: {data1}")
print(f"  Hash: {hash1}")

# Version 2: WITH checkoutoption at the end
data2 = f"{storename}{txndatetime}{chargetotal}{currency}{checkoutoption}"
hash2 = hmac.new(
    shared_secret.encode('utf-8'),
    data2.encode('utf-8'),
    hashlib.sha256
).hexdigest()
print(f"\nWITH checkoutoption at end:")
print(f"  Data: {data2}")
print(f"  Hash: {hash2}")

# Version 3: WITH checkoutoption after txntype (alphabetical)
# If sorted: chargetotal, checkoutoption, currency, storename, txndatetime
data3 = f"{chargetotal}{checkoutoption}{currency}{storename}{txndatetime}"
hash3 = hmac.new(
    shared_secret.encode('utf-8'),
    data3.encode('utf-8'),
    hashlib.sha256
).hexdigest()
print(f"\nALPHABETICAL ORDER with checkoutoption:")
print(f"  Data: {data3}")
print(f"  Hash: {hash3}")

# Version 4: Specific Fiserv order from docs
# storename|txndatetime|chargetotal|currency
data4 = f"{storename}|{txndatetime}|{chargetotal}|{currency}"
hash4 = hmac.new(
    shared_secret.encode('utf-8'),
    data4.encode('utf-8'),
    hashlib.sha256
).hexdigest()
print(f"\nWITH PIPE SEPARATORS (from some docs):")
print(f"  Data: {data4}")
print(f"  Hash: {hash4}")

print("\n" + "="*60)
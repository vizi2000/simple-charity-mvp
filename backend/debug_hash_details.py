#!/usr/bin/env python3
"""
Szczegółowa analiza co dokładnie wchodzi do hasha
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import hmac
import hashlib
import base64
from collections import OrderedDict

print("="*70)
print("ANALIZA SZCZEGÓŁOWA GENEROWANIA HASHA")
print("="*70)

# Różne strefy czasowe
warsaw_tz = ZoneInfo("Europe/Warsaw")
berlin_tz = ZoneInfo("Europe/Berlin")
utc_tz = ZoneInfo("UTC")

# Generuj timestampy
now_warsaw = datetime.now(warsaw_tz)
now_berlin = datetime.now(berlin_tz)
now_utc = datetime.now(utc_tz)

timestamp_warsaw = now_warsaw.strftime("%Y:%m:%d-%H:%M:%S")
timestamp_berlin = now_berlin.strftime("%Y:%m:%d-%H:%M:%S")
timestamp_utc = now_utc.strftime("%Y:%m:%d-%H:%M:%S")

print("\n📅 TIMESTAMPY DO TESTOWANIA:")
print(f"Warsaw:  {timestamp_warsaw}")
print(f"Berlin:  {timestamp_berlin}")
print(f"UTC:     {timestamp_utc}")

shared_secret = "j}2W3P)Lwv"
store_id = "760995999"

def generate_hash_variants(txndatetime, timezone_str):
    """Generuj hash z różnymi wariantami"""
    
    print(f"\n🔐 TEST DLA timezone={timezone_str}, txndatetime={txndatetime}")
    print("-" * 50)
    
    # Podstawowe pola
    form_fields = OrderedDict([
        ('storename', store_id),
        ('txntype', 'sale'),
        ('timezone', timezone_str),
        ('txndatetime', txndatetime),
        ('hash_algorithm', 'HMACSHA256'),
        ('chargetotal', '10.00'),
        ('currency', '985'),
        ('checkoutoption', 'combinedpage')
    ])
    
    # Wariant 1: Standardowy (bez hash_algorithm w stringu)
    exclude_fields = {'hash_algorithm', 'hashExtended', 'hash'}
    fields_for_hash1 = {k: v for k, v in form_fields.items() if k not in exclude_fields}
    sorted_fields1 = OrderedDict(sorted(fields_for_hash1.items()))
    hash_string1 = '|'.join(str(v) for v in sorted_fields1.values())
    
    print("\n  Wariant 1 - BEZ hash_algorithm:")
    print(f"  Pola: {list(sorted_fields1.keys())}")
    print(f"  String: {hash_string1[:100]}...")
    
    hash_bytes1 = hmac.new(
        shared_secret.encode('utf-8'),
        hash_string1.encode('utf-8'),
        hashlib.sha256
    ).digest()
    hash_value1 = base64.b64encode(hash_bytes1).decode('utf-8')
    print(f"  Hash: {hash_value1}")
    
    # Wariant 2: Z hash_algorithm w stringu
    fields_for_hash2 = {k: v for k, v in form_fields.items() if k not in {'hashExtended', 'hash'}}
    sorted_fields2 = OrderedDict(sorted(fields_for_hash2.items()))
    hash_string2 = '|'.join(str(v) for v in sorted_fields2.values())
    
    print("\n  Wariant 2 - Z hash_algorithm:")
    print(f"  Pola: {list(sorted_fields2.keys())}")
    print(f"  String: {hash_string2[:100]}...")
    
    hash_bytes2 = hmac.new(
        shared_secret.encode('utf-8'),
        hash_string2.encode('utf-8'),
        hashlib.sha256
    ).digest()
    hash_value2 = base64.b64encode(hash_bytes2).decode('utf-8')
    print(f"  Hash: {hash_value2}")
    
    # Wariant 3: Timezone na końcu (może kolejność ma znaczenie?)
    reordered = OrderedDict([
        ('chargetotal', '10.00'),
        ('checkoutoption', 'combinedpage'),
        ('currency', '985'),
        ('storename', store_id),
        ('timezone', timezone_str),
        ('txndatetime', txndatetime),
        ('txntype', 'sale')
    ])
    hash_string3 = '|'.join(str(v) for v in reordered.values())
    
    print("\n  Wariant 3 - Alfabetyczna kolejność kluczy:")
    print(f"  Pola: {list(reordered.keys())}")
    print(f"  String: {hash_string3[:100]}...")
    
    hash_bytes3 = hmac.new(
        shared_secret.encode('utf-8'),
        hash_string3.encode('utf-8'),
        hashlib.sha256
    ).digest()
    hash_value3 = base64.b64encode(hash_bytes3).decode('utf-8')
    print(f"  Hash: {hash_value3}")
    
    return hash_value1, hash_value2, hash_value3

# Test 1: Z czasem warszawskim i timezone Warsaw
print("\n" + "="*70)
print("TEST 1: Warsaw timezone + Warsaw time")
generate_hash_variants(timestamp_warsaw, "Europe/Warsaw")

# Test 2: Z czasem UTC ale timezone Warsaw
print("\n" + "="*70)
print("TEST 2: Warsaw timezone + UTC time (może tego oczekują?)")
generate_hash_variants(timestamp_utc, "Europe/Warsaw")

# Test 3: Z czasem warszawskim ale timezone Berlin
print("\n" + "="*70)
print("TEST 3: Berlin timezone + Warsaw time")
generate_hash_variants(timestamp_warsaw, "Europe/Berlin")

# Test 4: Może oczekują UTC?
print("\n" + "="*70)
print("TEST 4: UTC timezone + UTC time")
generate_hash_variants(timestamp_utc, "UTC")

print("\n" + "="*70)
print("SPRAWDZENIE PLIKÓW KONFIGURACYJNYCH")
print("="*70)

# Szukaj plików konfiguracyjnych
import os
import glob

config_patterns = [
    "*.env",
    "*.ini",
    "*.conf",
    "*.config",
    "*.yml",
    "*.yaml",
    "config.*",
    "settings.*"
]

print("\n🔍 Szukam plików konfiguracyjnych...")

for pattern in config_patterns:
    files = glob.glob(f"/Users/wojciechwiesner/simple mvp charity/backend/{pattern}")
    for file in files:
        if os.path.exists(file):
            print(f"\n📄 Znaleziono: {file}")
            # Sprawdź czy zawiera informacje o Fiserv
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    if 'fiserv' in content.lower() or '760995999' in content:
                        print("  ⚠️ Zawiera dane Fiserv!")
                        # Wyświetl relevantne linie
                        for line in content.split('\n'):
                            if 'fiserv' in line.lower() or 'secret' in line.lower() or 'store' in line.lower():
                                print(f"    {line[:100]}")
            except:
                pass

print("\n" + "="*70)
print("WNIOSKI")
print("="*70)
print("""
🤔 MOŻLIWE PROBLEMY:

1. Hash może używać INNEGO czasu niż wysyłany:
   - Wysyłamy Warsaw time, ale hash z UTC?
   - Albo odwrotnie?

2. Kolejność pól w hash stringu:
   - Może musi być konkretna kolejność?
   - Alfabetyczna po kluczu czy wartości?

3. Które pola wchodzą do hasha:
   - Z hash_algorithm czy bez?
   - Może jakieś ukryte pola?

4. Format timezone w hashu:
   - "Europe/Warsaw" czy może "CEST"?
   - Czy w ogóle timezone wchodzi do hasha?

5. Dane z plików konfiguracyjnych:
   - Może jest inny secret w .env?
   - Może są dodatkowe parametry?
""")
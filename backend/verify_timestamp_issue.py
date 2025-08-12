#!/usr/bin/env python3
"""
Weryfikacja problemu z timestampem
Może w przykładzie był UTC zamiast Warsaw?
"""

import hmac
import hashlib
import base64
from collections import OrderedDict
from datetime import datetime
from zoneinfo import ZoneInfo


def test_timestamp_variations():
    """Test różnych wersji timestampa"""
    
    print("="*70)
    print("TEST RÓŻNYCH TIMESTAMPÓW")
    print("="*70)
    
    # Podstawowe dane (bez timestampa)
    base_fields = OrderedDict([
        ('storename', '760995999'),
        ('txntype', 'sale'),
        ('timezone', 'Europe/Warsaw'),
        ('chargetotal', '50.00'),
        ('currency', '985'),
        ('checkoutoption', 'combinedpage'),
        ('oid', 'd4742929-665f-4a8e-a696-2fc2717841dc'),
        ('responseSuccessURL', 'https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=success'),
        ('responseFailURL', 'https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=failure'),
        ('transactionNotificationURL', 'https://charity-webhook.ngrok.app/api/webhooks/fiserv'),
        ('bname', 'Jan Kowalski'),
        ('bemail', 'jan.kowalski@example.com')
    ])
    
    expected_hash_start = "7xQK8PzVh9mJ4kL2nF6sT3wRyD5gE1aB0cU"
    secret = "j}2W3P)Lwv"
    
    # Różne wersje timestampa do przetestowania
    # Oryginalny timestamp: 2025:07:28-22:15:45 (Warsaw)
    # Ale może był wysłany jako UTC (20:15:45)?
    
    timestamps = [
        ("Oryginalny (22:15 Warsaw)", "2025:07:28-22:15:45"),
        ("UTC -2h (20:15)", "2025:07:28-20:15:45"),
        ("UTC -1h letni (21:15)", "2025:07:28-21:15:45"),
        ("Bez timestampa", None),
        ("Berlin time (21:15)", "2025:07:28-21:15:45"),
        ("Data odwrotnie", "28:07:2025-22:15:45"),
        ("Format ISO", "2025-07-28T22:15:45"),
        ("Format US", "07/28/2025 22:15:45"),
    ]
    
    # Test też z Europe/Berlin
    timezones = [
        ("Europe/Warsaw", "Europe/Warsaw"),
        ("Europe/Berlin", "Europe/Berlin"),
        ("UTC", "UTC"),
        ("Puste", ""),
    ]
    
    print(f"\n🎯 Szukamy hasha: {expected_hash_start}...")
    
    for tz_name, tz_value in timezones:
        print(f"\n🌍 Timezone: {tz_name}")
        print("-" * 50)
        
        for ts_name, ts_value in timestamps:
            fields = base_fields.copy()
            fields['timezone'] = tz_value
            
            if ts_value is not None:
                fields['txndatetime'] = ts_value
            
            # Sortuj alfabetycznie
            sorted_fields = OrderedDict(sorted(fields.items()))
            
            # String do hasha (tylko wartości)
            hash_string = '|'.join(str(v) for v in sorted_fields.values())
            
            # Oblicz hash
            hash_bytes = hmac.new(
                secret.encode('utf-8'),
                hash_string.encode('utf-8'),
                hashlib.sha256
            ).digest()
            hash_base64 = base64.b64encode(hash_bytes).decode('utf-8')
            
            if hash_base64.startswith(expected_hash_start):
                print(f"✅ ZNALEZIONO! {ts_name}")
                print(f"   Timezone: {tz_value}")
                print(f"   Timestamp: {ts_value}")
                print(f"   Hash: {hash_base64}")
                print(f"\n   String do hasha:")
                print(f"   {hash_string}")
                return tz_value, ts_value, hash_base64
            else:
                print(f"❌ {ts_name:25} -> {hash_base64[:20]}...")
    
    print("\n" + "="*70)
    print("NIE ZNALEZIONO KOMBINACJI")
    print("="*70)
    
    # Może problem jest z URLami?
    print("\n🔍 TEST Z RÓŻNYMI FORMATAMI URL...")
    
    # Może URLe były zakodowane inaczej?
    url_tests = [
        ("Bez query params", 
         "https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status",
         "https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status"),
        ("Z &amp;", 
         "https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=success&amp;test=1",
         "https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=failure&amp;test=1"),
        ("Localhost", 
         "http://localhost:5174/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=success",
         "http://localhost:5174/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=failure"),
    ]
    
    for url_name, success_url, fail_url in url_tests:
        fields = base_fields.copy()
        fields['timezone'] = 'Europe/Warsaw'
        fields['txndatetime'] = '2025:07:28-22:15:45'
        fields['responseSuccessURL'] = success_url
        fields['responseFailURL'] = fail_url
        
        sorted_fields = OrderedDict(sorted(fields.items()))
        hash_string = '|'.join(str(v) for v in sorted_fields.values())
        
        hash_bytes = hmac.new(
            secret.encode('utf-8'),
            hash_string.encode('utf-8'),
            hashlib.sha256
        ).digest()
        hash_base64 = base64.b64encode(hash_bytes).decode('utf-8')
        
        if hash_base64.startswith(expected_hash_start):
            print(f"✅ ZNALEZIONO! URLs: {url_name}")
            print(f"   Hash: {hash_base64}")
            return 'Europe/Warsaw', '2025:07:28-22:15:45', hash_base64
        else:
            print(f"❌ URLs {url_name:20} -> {hash_base64[:20]}...")
    
    return None, None, None


if __name__ == "__main__":
    result = test_timestamp_variations()
    
    if result[0]:
        tz, ts, hash_val = result
        print("\n" + "="*70)
        print("✅ ZNALEZIONO POPRAWNĄ KOMBINACJĘ!")
        print("="*70)
        print(f"Timezone: {tz}")
        print(f"Timestamp: {ts}")
        print(f"Hash: {hash_val}")
    else:
        print("\n❌ Hash z przykładu może być niepoprawny!")
        print("Lub używają innego shared secret niż 'j}2W3P)Lwv'")
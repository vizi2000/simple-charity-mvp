#!/usr/bin/env python3
"""
Weryfikacja obliczania hash - sprawdzenie kolejności pól
"""

import hmac
import hashlib
import base64
from collections import OrderedDict

# Dane z przykładu
SHARED_SECRET = "j}2W3P)Lwv"

# Pola z formularza DEBUG
form_fields = {
    'chargetotal': '10.00',
    'checkoutoption': 'classic',
    'currency': '985',
    'oid': 'DEBUG-20250729002249',
    'responseFailURL': 'https://example.com/failure',
    'responseSuccessURL': 'https://example.com/success',
    'storename': '760995999',
    'timezone': 'Europe/Berlin',
    'txndatetime': '2025:07:28-22:22:49',
    'txntype': 'sale'
}

def calculate_hash(fields, secret):
    """Oblicz hash z podanych pól"""
    # Sortuj alfabetycznie
    sorted_fields = sorted(fields.items())
    
    # Łącz TYLKO WARTOŚCI
    values = '|'.join(str(v) for k, v in sorted_fields)
    
    # Oblicz HMAC-SHA256
    hash_bytes = hmac.new(
        secret.encode('utf-8'),
        values.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Base64
    return base64.b64encode(hash_bytes).decode('utf-8'), values

print("="*60)
print("WERYFIKACJA OBLICZANIA HASH")
print("="*60)

# Test 1: Nasza metoda (alfabetycznie)
print("\n1. NASZA METODA (alfabetycznie):")
print("Kolejność pól:")
for k, v in sorted(form_fields.items()):
    print(f"  {k}: {v}")

hash_result, hash_string = calculate_hash(form_fields, SHARED_SECRET)
print(f"\nHash string:\n{hash_string}")
print(f"\nWynikowy hash:\n{hash_result}")
print(f"\nHash z formularza:\n6VqoWrXmjHizIhHPbn8zkvkohd9uvvQ0o9fIxULAKyk=")
print(f"\nCzy się zgadza? {'TAK' if hash_result == '6VqoWrXmjHizIhHPbn8zkvkohd9uvvQ0o9fIxULAKyk=' else 'NIE'}")

# Test 2: Tylko podstawowe pola (bez response URLs)
print("\n" + "="*60)
print("2. BEZ RESPONSE URLs:")
basic_fields = {k: v for k, v in form_fields.items() if 'response' not in k.lower()}
print("Pola:")
for k, v in sorted(basic_fields.items()):
    print(f"  {k}: {v}")

hash_result2, hash_string2 = calculate_hash(basic_fields, SHARED_SECRET)
print(f"\nHash string:\n{hash_string2}")
print(f"\nWynikowy hash:\n{hash_result2}")

# Test 3: Dokładnie jak w analizie użytkownika
print("\n" + "="*60)
print("3. KOLEJNOŚĆ Z ANALIZY:")
analysis_order = [
    'chargetotal', 'checkoutoption', 'currency', 'oid', 
    'responseFailURL', 'responseSuccessURL', 'storename', 
    'timezone', 'txndatetime', 'txntype'
]

# String dokładnie z analizy
analysis_string = "10.00|classic|985|DEBUG-20250729002249|https://example.com/failure|https://example.com/success|760995999|Europe/Berlin|2025:07:28-22:22:49|sale"

print(f"\nString z analizy:\n{analysis_string}")

# Oblicz hash
hash_bytes = hmac.new(
    SHARED_SECRET.encode('utf-8'),
    analysis_string.encode('utf-8'),
    hashlib.sha256
).digest()
expected_hash = base64.b64encode(hash_bytes).decode('utf-8')

print(f"\nOczekiwany hash (z analizy):\n6VqoWrXmjHizIhHPbn8zkvkohd9uvvQ0o9fIxULAKyk=")
print(f"\nObliczony hash:\n{expected_hash}")
print(f"\nCzy się zgadza? {'TAK' if expected_hash == '6VqoWrXmjHizIhHPbn8zkvkohd9uvvQ0o9fIxULAKyk=' else 'NIE'}")

# Test 4: Nasza kolejność vs analiza
print("\n" + "="*60)
print("4. PORÓWNANIE KOLEJNOŚCI:")
print("\nNasza kolejność (alfabetyczna):")
our_order = [k for k, v in sorted(form_fields.items())]
print(our_order)

print("\nKolejność z analizy:")
print(analysis_order)

print("\nCzy kolejność jest taka sama?", our_order == analysis_order)

# Generuj poprawny string
print("\n" + "="*60)
print("5. POPRAWNY HASH STRING:")
correct_values = []
for key in sorted(form_fields.keys()):
    correct_values.append(form_fields[key])
    
correct_string = '|'.join(correct_values)
print(f"\nPoprawny string do hash:\n{correct_string}")

# Oblicz poprawny hash
correct_hash_bytes = hmac.new(
    SHARED_SECRET.encode('utf-8'),
    correct_string.encode('utf-8'),
    hashlib.sha256
).digest()
correct_hash = base64.b64encode(correct_hash_bytes).decode('utf-8')

print(f"\nPoprawny hash:\n{correct_hash}")
print(f"\nCzy to jest hash z analizy? {'TAK' if correct_hash == '6VqoWrXmjHizIhHPbn8zkvkohd9uvvQ0o9fIxULAKyk=' else 'NIE'}")
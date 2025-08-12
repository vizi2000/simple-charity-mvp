#!/usr/bin/env python3
"""
GŁĘBOKA ANALIZA GENEROWANIA HASHA
Sprawdzenie czy hash jest generowany z dokładnie tych samych pól które są wysyłane
"""

import hmac
import hashlib
import base64
from collections import OrderedDict


def analyze_hash_generation():
    """Dokładna analiza generowania hasha"""
    
    print("="*70)
    print("GŁĘBOKA ANALIZA GENEROWANIA HASHA FISERV")
    print("="*70)
    
    # DOKŁADNE dane z przykładu Fiserv
    example_fields = OrderedDict([
        ('storename', '760995999'),
        ('txntype', 'sale'),
        ('timezone', 'Europe/Warsaw'),
        ('txndatetime', '2025:07:28-22:15:45'),
        ('chargetotal', '50.00'),
        ('currency', '985'),
        ('checkoutoption', 'combinedpage'),
        ('oid', 'd4742929-665f-4a8e-a696-2fc2717841dc'),
        ('responseSuccessURL', 'https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=success'),
        ('responseFailURL', 'https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=failure'),
        ('transactionNotificationURL', 'https://charity-webhook.ngrok.app/api/webhooks/fiserv'),
        ('bname', 'Jan Kowalski'),
        ('bemail', 'jan.kowalski@example.com'),
        ('hash_algorithm', 'HMACSHA256'),
        ('hashExtended', '7xQK8PzVh9mJ4kL2nF6sT3wRyD5gE1aB0cU...')
    ])
    
    print("\n📋 POLA Z PRZYKŁADU FISERV:")
    print("-" * 50)
    for key, value in example_fields.items():
        if key == 'hashExtended':
            print(f"{key:30} = {value[:20]}...")
        else:
            print(f"{key:30} = {value}")
    
    # KROK 1: Określ które pola wchodzą do hasha
    print("\n" + "="*70)
    print("KROK 1: KTÓRE POLA WCHODZĄ DO HASHA?")
    print("="*70)
    
    # Pola które NIE wchodzą do hasha według dokumentacji
    exclude_from_hash = {'hash_algorithm', 'hashExtended', 'hash'}
    
    # Pola do hasha
    fields_for_hash = OrderedDict()
    for key, value in example_fields.items():
        if key not in exclude_from_hash:
            fields_for_hash[key] = value
    
    print("\n✅ POLA DO HASHA (bez hash_algorithm i hashExtended):")
    for i, (key, value) in enumerate(fields_for_hash.items(), 1):
        print(f"{i:2}. {key:30} = {value[:50]}...")
    
    # KROK 2: Sortowanie alfabetyczne
    print("\n" + "="*70)
    print("KROK 2: SORTOWANIE ALFABETYCZNE")
    print("="*70)
    
    sorted_fields = OrderedDict(sorted(fields_for_hash.items()))
    
    print("\n📝 POLA PO SORTOWANIU ALFABETYCZNYM:")
    for i, (key, value) in enumerate(sorted_fields.items(), 1):
        print(f"{i:2}. {key:30} = {value[:50]}...")
    
    # KROK 3: Tworzenie stringu do hasha
    print("\n" + "="*70)
    print("KROK 3: TWORZENIE STRINGU DO HASHA")
    print("="*70)
    
    # Metoda 1: Tylko wartości (jak w dokumentacji)
    values_only = '|'.join(str(value) for value in sorted_fields.values())
    
    print("\n🔹 METODA 1: Tylko wartości (pipe-separated):")
    print("-" * 50)
    print(f"Długość: {len(values_only)} znaków")
    print(f"Pierwsze 200 znaków:")
    print(values_only[:200])
    print("...")
    print(f"Ostatnie 100 znaków:")
    print(values_only[-100:])
    
    # Metoda 2: Klucz=wartość (alternatywna)
    key_value_pairs = '|'.join(f"{key}={value}" for key, value in sorted_fields.items())
    
    print("\n🔹 METODA 2: Klucz=wartość (alternatywna):")
    print("-" * 50)
    print(f"Długość: {len(key_value_pairs)} znaków")
    print(f"Pierwsze 200 znaków:")
    print(key_value_pairs[:200])
    
    # KROK 4: Obliczanie hasha
    print("\n" + "="*70)
    print("KROK 4: OBLICZANIE HASHA")
    print("="*70)
    
    shared_secret = "j}2W3P)Lwv"
    
    print(f"\n🔑 Shared Secret: {shared_secret}")
    
    # Hash dla metody 1 (tylko wartości)
    hash1 = hmac.new(
        shared_secret.encode('utf-8'),
        values_only.encode('utf-8'),
        hashlib.sha256
    ).digest()
    hash1_base64 = base64.b64encode(hash1).decode('utf-8')
    
    print(f"\n📊 METODA 1 - Hash (tylko wartości):")
    print(f"   Base64: {hash1_base64}")
    print(f"   Długość: {len(hash1_base64)} znaków")
    
    # Hash dla metody 2 (klucz=wartość)
    hash2 = hmac.new(
        shared_secret.encode('utf-8'),
        key_value_pairs.encode('utf-8'),
        hashlib.sha256
    ).digest()
    hash2_base64 = base64.b64encode(hash2).decode('utf-8')
    
    print(f"\n📊 METODA 2 - Hash (klucz=wartość):")
    print(f"   Base64: {hash2_base64}")
    print(f"   Długość: {len(hash2_base64)} znaków")
    
    # KROK 5: Weryfikacja kolejności pól
    print("\n" + "="*70)
    print("KROK 5: WERYFIKACJA KOLEJNOŚCI PÓL")
    print("="*70)
    
    print("\n🔍 KOLEJNOŚĆ ALFABETYCZNA (ważne!):")
    expected_order = [
        'bemail',
        'bname', 
        'chargetotal',
        'checkoutoption',
        'currency',
        'oid',
        'responseFailURL',
        'responseSuccessURL',
        'storename',
        'timezone',
        'transactionNotificationURL',
        'txndatetime',
        'txntype'
    ]
    
    actual_order = list(sorted_fields.keys())
    
    print("\nOczekiwana kolejność:")
    for i, field in enumerate(expected_order, 1):
        print(f"  {i:2}. {field}")
    
    print("\nRzeczywista kolejność:")
    for i, field in enumerate(actual_order, 1):
        match = "✅" if i <= len(expected_order) and field == expected_order[i-1] else "❌"
        print(f"  {i:2}. {field} {match}")
    
    # KROK 6: Szczegółowa analiza stringu
    print("\n" + "="*70)
    print("KROK 6: SZCZEGÓŁOWA ANALIZA STRINGU DO HASHA")
    print("="*70)
    
    print("\n📝 PEŁNY STRING DO HASHA (metoda 1 - tylko wartości):")
    print("-" * 50)
    
    # Rozbij na części dla lepszej czytelności
    values_list = list(sorted_fields.values())
    for i, (key, value) in enumerate(sorted_fields.items()):
        print(f"{i+1:2}. [{key}]: {value}")
    
    print("\n🔗 ZŁĄCZONY STRING:")
    print(values_only)
    
    # KROK 7: Problemy do sprawdzenia
    print("\n" + "="*70)
    print("⚠️ POTENCJALNE PROBLEMY DO SPRAWDZENIA:")
    print("="*70)
    
    print("""
1. ❓ Czy URLe są dokładnie takie same?
   - Czy nie ma dodatkowych spacji?
   - Czy nie ma zakodowanych znaków (&amp; zamiast &)?
   
2. ❓ Czy timestamp jest aktualny?
   - Hash musi być generowany z TYM SAMYM timestampem który jest wysyłany
   
3. ❓ Czy wszystkie pola są uwzględnione?
   - Czy nie brakuje żadnego pola?
   - Czy nie ma dodatkowych pól?
   
4. ❓ Czy kolejność jest alfabetyczna?
   - Sortowanie MUSI być alfabetyczne po KLUCZU
   
5. ❓ Czy shared secret jest poprawny?
   - "j}2W3P)Lwv" - czy to na pewno aktualny secret?
    """)
    
    return {
        'fields_for_hash': fields_for_hash,
        'sorted_fields': sorted_fields,
        'hash_string': values_only,
        'calculated_hash': hash1_base64
    }


def test_our_implementation():
    """Test naszej implementacji z tymi samymi danymi"""
    
    print("\n" + "="*70)
    print("TEST NASZEJ IMPLEMENTACJI")
    print("="*70)
    
    from fiserv_payment_v2 import FiservIPGPayment
    
    client = FiservIPGPayment()
    
    # Użyj dokładnie tych samych danych
    test_fields = {
        'storename': '760995999',
        'txntype': 'sale',
        'timezone': 'Europe/Warsaw',
        'txndatetime': '2025:07:28-22:15:45',
        'chargetotal': '50.00',
        'currency': '985',
        'checkoutoption': 'combinedpage',
        'oid': 'd4742929-665f-4a8e-a696-2fc2717841dc',
        'responseSuccessURL': 'https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=success',
        'responseFailURL': 'https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=failure',
        'transactionNotificationURL': 'https://charity-webhook.ngrok.app/api/webhooks/fiserv',
        'bname': 'Jan Kowalski',
        'bemail': 'jan.kowalski@example.com',
        'hash_algorithm': 'HMACSHA256'
    }
    
    # Oblicz hash używając naszej metody
    our_hash = client.calculate_hash(test_fields)
    
    print(f"\n🔧 NASZ HASH:")
    print(f"   {our_hash}")
    
    # Porównaj z przykładem
    example_hash_fragment = "7xQK8PzVh9mJ4kL2nF6sT3wRyD5gE1aB0cU"
    
    if our_hash.startswith(example_hash_fragment):
        print(f"\n✅ HASH ZGADZA SIĘ Z PRZYKŁADEM!")
    else:
        print(f"\n❌ HASH NIE ZGADZA SIĘ!")
        print(f"   Oczekiwany początek: {example_hash_fragment}...")
        print(f"   Nasz początek:       {our_hash[:36]}...")
    
    return our_hash


if __name__ == "__main__":
    # Analiza
    result = analyze_hash_generation()
    
    # Test naszej implementacji
    our_hash = test_our_implementation()
    
    print("\n" + "="*70)
    print("WNIOSKI")
    print("="*70)
    
    print("""
🎯 KRYTYCZNE PUNKTY:
1. Hash musi być generowany z pól POSORTOWANYCH alfabetycznie
2. Do hasha wchodzą WSZYSTKIE pola OPRÓCZ: hash_algorithm, hashExtended
3. String to TYLKO WARTOŚCI połączone znakiem |
4. Timestamp w hashu MUSI być identyczny z wysyłanym
    """)
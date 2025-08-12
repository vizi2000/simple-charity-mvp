#!/usr/bin/env python3
"""
Znajdź poprawną metodę generowania hasha
Testuj różne kombinacje aż znajdziesz tę która daje hash z przykładu
"""

import hmac
import hashlib
import base64
from collections import OrderedDict


def test_hash_methods():
    """Testuj różne metody generowania hasha"""
    
    print("="*70)
    print("SZUKANIE POPRAWNEJ METODY GENEROWANIA HASHA")
    print("="*70)
    
    # Dane z przykładu (BEZ hash_algorithm i hashExtended)
    fields = OrderedDict([
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
        ('bemail', 'jan.kowalski@example.com')
    ])
    
    # Oczekiwany hash (początek)
    expected_hash_start = "7xQK8PzVh9mJ4kL2nF6sT3wRyD5gE1aB0cU"
    
    # Różne shared secrets do przetestowania
    secrets = [
        "j}2W3P)Lwv",  # Oryginalny
        "c7dP/$5PBx",  # Alternatywny z .env
        "aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG",  # REST API secret
    ]
    
    print(f"\n🎯 Szukamy hasha zaczynającego się od: {expected_hash_start}...")
    
    # Test różnych metod
    methods = []
    
    # METODA 1: Alfabetycznie, tylko wartości
    sorted_fields = OrderedDict(sorted(fields.items()))
    method1_string = '|'.join(str(v) for v in sorted_fields.values())
    methods.append(("Alfabetycznie, tylko wartości", method1_string))
    
    # METODA 2: Alfabetycznie, klucz=wartość
    method2_string = '|'.join(f"{k}={v}" for k, v in sorted_fields.items())
    methods.append(("Alfabetycznie, klucz=wartość", method2_string))
    
    # METODA 3: Oryginalna kolejność, tylko wartości
    method3_string = '|'.join(str(v) for v in fields.values())
    methods.append(("Oryginalna kolejność, tylko wartości", method3_string))
    
    # METODA 4: Oryginalna kolejność, klucz=wartość
    method4_string = '|'.join(f"{k}={v}" for k, v in fields.items())
    methods.append(("Oryginalna kolejność, klucz=wartość", method4_string))
    
    # METODA 5: Alfabetycznie, wartości połączone bez separatora
    method5_string = ''.join(str(v) for v in sorted_fields.values())
    methods.append(("Alfabetycznie, bez separatora", method5_string))
    
    # METODA 6: String jak w dokumentacji (może być inny format timestampa)
    # Spróbuj z timestampem w formacie ISO
    fields_alt = fields.copy()
    fields_alt['txndatetime'] = '2025-07-28T22:15:45'
    sorted_alt = OrderedDict(sorted(fields_alt.items()))
    method6_string = '|'.join(str(v) for v in sorted_alt.values())
    methods.append(("Z ISO timestamp", method6_string))
    
    # METODA 7: Może hash_algorithm też wchodzi do hasha?
    fields_with_algo = fields.copy()
    fields_with_algo['hash_algorithm'] = 'HMACSHA256'
    sorted_with_algo = OrderedDict(sorted(fields_with_algo.items()))
    method7_string = '|'.join(str(v) for v in sorted_with_algo.values())
    methods.append(("Z hash_algorithm w hashu", method7_string))
    
    # METODA 8: Może są dodatkowe pola które nie widzimy?
    # Na przykład może być pusty parametr lub coś podobnego
    
    found = False
    
    for secret_name, secret in [("Oryginalny", secrets[0]), ("Alternatywny", secrets[1]), ("REST API", secrets[2])]:
        print(f"\n🔑 Testowanie z secretem: {secret_name} ({secret[:10]}...)")
        print("-" * 50)
        
        for method_name, hash_string in methods:
            # Oblicz hash
            hash_bytes = hmac.new(
                secret.encode('utf-8'),
                hash_string.encode('utf-8'),
                hashlib.sha256
            ).digest()
            hash_base64 = base64.b64encode(hash_bytes).decode('utf-8')
            
            # Sprawdź czy zgadza się
            if hash_base64.startswith(expected_hash_start):
                print(f"✅ ZNALEZIONO! Metoda: {method_name}")
                print(f"   Hash: {hash_base64}")
                print(f"   Secret: {secret}")
                print(f"\n   String do hasha:")
                print(f"   {hash_string[:200]}...")
                found = True
                return secret, method_name, hash_string, hash_base64
            else:
                print(f"❌ {method_name[:30]:30} -> {hash_base64[:20]}...")
    
    if not found:
        print("\n" + "="*70)
        print("❌ NIE ZNALEZIONO PASUJĄCEJ METODY")
        print("="*70)
        
        # Może problem jest gdzie indziej?
        print("\n🤔 MOŻLIWE PRZYCZYNY:")
        print("""
1. Shared secret jest inny niż testowane
2. Kolejność pól jest inna
3. Są dodatkowe pola których nie widzimy
4. Format niektórych pól jest inny (np. URLe)
5. Hash w przykładzie może być błędny
        """)
        
        # Spróbuj odgadnąć secret metodą brute-force dla znanego hasha
        print("\n🔍 PRÓBA ODGADNIĘCIA SECRETU...")
        
        # Użyj metody 1 (alfabetycznie, tylko wartości)
        test_string = method1_string
        
        # Lista możliwych secretów do przetestowania
        possible_secrets = [
            "j}2W3P)Lwv",
            "c7dP/$5PBx",
            "aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG",
            "test",
            "secret",
            "password",
            "760995999",  # Może store ID?
            "HMACSHA256",  # Może algorytm?
            "Fiserv2024",
            "PolCard",
            "IPGConnect"
        ]
        
        print(f"\nTestowanie {len(possible_secrets)} możliwych secretów...")
        
        for test_secret in possible_secrets:
            test_hash = base64.b64encode(
                hmac.new(
                    test_secret.encode('utf-8'),
                    test_string.encode('utf-8'),
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')
            
            if test_hash.startswith(expected_hash_start):
                print(f"✅ ZNALEZIONO SECRET: {test_secret}")
                print(f"   Hash: {test_hash}")
                return test_secret, "Alfabetycznie, tylko wartości", test_string, test_hash
    
    return None, None, None, None


if __name__ == "__main__":
    result = test_hash_methods()
    
    if result[0]:
        secret, method, hash_string, calculated_hash = result
        
        print("\n" + "="*70)
        print("✅ ROZWIĄZANIE ZNALEZIONE!")
        print("="*70)
        
        print(f"\n📝 Poprawna metoda: {method}")
        print(f"🔑 Poprawny secret: {secret}")
        print(f"📊 Wygenerowany hash: {calculated_hash}")
        
        print("\n🔧 IMPLEMENTACJA:")
        print("""
# Poprawna metoda generowania hasha:
1. Weź wszystkie pola OPRÓCZ hash_algorithm i hashExtended
2. Posortuj alfabetycznie po KLUCZU
3. Weź tylko WARTOŚCI
4. Połącz znakiem |
5. Oblicz HMAC-SHA256 z odpowiednim secretem
6. Zakoduj w Base64
        """)
    else:
        print("\n❌ Nie udało się znaleźć poprawnej metody!")
        print("Może przykładowy hash jest niepoprawny lub brakuje informacji?")
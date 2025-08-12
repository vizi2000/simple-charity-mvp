#!/usr/bin/env python3
"""
Porównanie naszych pól z przykładem od Fiserv
"""

from datetime import datetime
from zoneinfo import ZoneInfo

# Przykład od Fiserv (z emaila)
fiserv_example = {
    'storename': '760995999',
    'txntype': 'sale',
    'timezone': 'Europe/Warsaw',
    'txndatetime': '2025:07:28-22:15:45',  # To był przykład
    'chargetotal': '50.00',
    'currency': '985',
    'checkoutoption': 'combinedpage',
    'oid': 'd4742929-665f-4a8e-a696-2fc2717841dc',
    'responseSuccessURL': 'https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=success',
    'responseFailURL': 'https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=failure',
    'transactionNotificationURL': 'https://charity-webhook.ngrok.app/api/webhooks/fiserv',
    'bname': 'Jan Kowalski',
    'bemail': 'jan.kowalski@example.com',
    'hash_algorithm': 'HMACSHA256',
    'hashExtended': '7xQK8PzVh9mJ4kL2nF6sT3wRyD5gE1aB0cU...'
}

# Nasze aktualne pola
our_fields = {
    'bemail': 'jan@example.com',
    'bname': 'Jan Kowalski',
    'chargetotal': '10.00',
    'checkoutoption': 'combinedpage',
    'currency': '985',
    'hashExtended': 'bMaHIWM/19jWcMCv2+Bc...',
    'hash_algorithm': 'HMACSHA256',
    'oid': 'DEBUG-20250809064114',
    'responseFailURL': 'https://charity.ngrok.app/failure',
    'responseSuccessURL': 'https://charity.ngrok.app/success',
    'storename': '760995999',
    'timezone': 'Europe/Warsaw',
    'transactionNotificationURL': 'https://charity-webhook.ngrok.app/webhook',
    'txndatetime': '2025:08:09-06:41:14',
    'txntype': 'sale'
}

print("="*60)
print("PORÓWNANIE Z PRZYKŁADEM FISERV")
print("="*60)

# Znajdź różnice
print("\n📊 ANALIZA RÓŻNIC:")
print("-" * 40)

# Pola które są w przykładzie ale nie u nas
missing_in_ours = set(fiserv_example.keys()) - set(our_fields.keys())
if missing_in_ours:
    print("\n❌ BRAKUJĄCE POLA (są w przykładzie, nie ma u nas):")
    for field in missing_in_ours:
        print(f"   - {field}: {fiserv_example[field]}")
else:
    print("\n✅ Nie brakuje żadnych pól z przykładu")

# Pola które mamy ale nie ma w przykładzie
extra_in_ours = set(our_fields.keys()) - set(fiserv_example.keys())
if extra_in_ours:
    print("\n⚠️ DODATKOWE POLA (mamy, ale nie ma w przykładzie):")
    for field in extra_in_ours:
        print(f"   - {field}: {our_fields[field]}")

# Porównaj wartości wspólnych pól
print("\n🔍 PORÓWNANIE WARTOŚCI:")
print("-" * 40)

differences = []
for field in sorted(set(fiserv_example.keys()) & set(our_fields.keys())):
    if field in ['hashExtended', 'txndatetime', 'oid', 'chargetotal']:
        # Te pola się różnią z definicji
        continue
    
    if field in ['responseSuccessURL', 'responseFailURL', 'transactionNotificationURL']:
        # URLs mogą się różnić w szczegółach
        fiserv_val = fiserv_example[field]
        our_val = our_fields[field]
        
        # Sprawdź główną domenę
        if 'ngrok' in fiserv_val and 'ngrok' in our_val:
            print(f"✅ {field}: OK (oba używają ngrok)")
        else:
            differences.append(f"{field}: różne domeny")
            print(f"⚠️ {field}:")
            print(f"   Fiserv: {fiserv_val[:50]}...")
            print(f"   My:     {our_val[:50]}...")
    
    elif field in ['bname', 'bemail']:
        # Dane klienta mogą się różnić
        continue
    
    else:
        fiserv_val = fiserv_example[field]
        our_val = our_fields[field]
        
        if fiserv_val != our_val:
            differences.append(f"{field}: '{fiserv_val}' vs '{our_val}'")
            print(f"❌ {field}:")
            print(f"   Fiserv: {fiserv_val}")
            print(f"   My:     {our_val}")
        else:
            print(f"✅ {field}: {our_val}")

# Sprawdź kolejność pól do hasha
print("\n📝 KOLEJNOŚĆ PÓL DO HASHA:")
print("-" * 40)

# Pola używane do hasha (alfabetycznie, bez hash_algorithm i hashExtended)
hash_fields_fiserv = sorted([k for k in fiserv_example.keys() 
                            if k not in ['hash_algorithm', 'hashExtended']])
hash_fields_ours = sorted([k for k in our_fields.keys() 
                          if k not in ['hash_algorithm', 'hashExtended']])

print("Fiserv używa pól:")
for field in hash_fields_fiserv:
    print(f"   {field}")

print("\nMy używamy pól:")
for field in hash_fields_ours:
    print(f"   {field}")

if hash_fields_fiserv == hash_fields_ours:
    print("\n✅ Kolejność i lista pól do hasha jest identyczna")
else:
    print("\n❌ Różnice w polach do hasha!")

# String do hasha - przykład
print("\n🔐 PRZYKŁAD STRINGU DO HASHA:")
print("-" * 40)

# Dla przykładu Fiserv
fiserv_hash_values = [fiserv_example[k] for k in hash_fields_fiserv]
fiserv_hash_string = '|'.join(fiserv_hash_values)
print("Fiserv (pierwsze 150 znaków):")
print(f"{fiserv_hash_string[:150]}...")

# Dla nas
our_hash_values = [our_fields[k] for k in hash_fields_ours]
our_hash_string = '|'.join(our_hash_values)
print("\nNasz (pierwsze 150 znaków):")
print(f"{our_hash_string[:150]}...")

# Podsumowanie
print("\n" + "="*60)
print("PODSUMOWANIE:")
print("="*60)

if not missing_in_ours and not differences:
    print("✅ Struktura danych jest zgodna z przykładem Fiserv")
    print("   Wszystkie wymagane pola są obecne")
    print("   Formaty są poprawne")
    
    print("\n🎯 PRAWDOPODOBNA PRZYCZYNA BŁĘDU:")
    print("   Problem nie jest w strukturze danych, ale w:")
    print("   1. Hash - może być nieprawidłowy shared secret")
    print("   2. Timestamp - mimo że format jest OK, może być problem z synchronizacją czasu")
    print("   3. Konfiguracja konta - brak uprawnień do Combined Page")
else:
    print("❌ Znaleziono różnice:")
    if missing_in_ours:
        print(f"   Brakuje {len(missing_in_ours)} pól")
    if differences:
        for diff in differences:
            print(f"   - {diff}")
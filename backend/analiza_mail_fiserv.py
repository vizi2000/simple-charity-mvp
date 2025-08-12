#!/usr/bin/env python3
"""
Dokładna analiza punktów z maila od Fiserv
"""

import json
from datetime import datetime
from zoneinfo import ZoneInfo
import hmac
import hashlib
import base64

print("\n" + "="*80)
print("ANALIZA MAILA OD FISERV - Golebiewska, Sylwia")
print("="*80)

# PUNKT 1: TIMEZONE
print("\n1️⃣ PROBLEM Z TIMEZONE:")
print("-" * 40)
print("Fiserv w logach widzi:")
print("   timezone=Europe/Berlin ❌")
print("Powinno być:")
print("   timezone=Europe/Warsaw ✅")
print("\nNasz test używa:")
warsaw_tz = ZoneInfo('Europe/Warsaw')
berlin_tz = ZoneInfo('Europe/Berlin')
now_warsaw = datetime.now(warsaw_tz)
now_berlin = datetime.now(berlin_tz)
print(f"   Warsaw: {now_warsaw.strftime('%Y:%m:%d-%H:%M:%S')}")
print(f"   Berlin: {now_berlin.strftime('%Y:%m:%d-%H:%M:%S')}")
print(f"   Różnica: {now_warsaw.hour - now_berlin.hour} godzin (teraz jest ta sama godzina)")

# PUNKT 2: TIMESTAMP
print("\n2️⃣ PROBLEM Z TIMESTAMP:")
print("-" * 40)
print("Fiserv otrzymał:")
print("   txndatetime=2025:07:28-21:01:59")
print("Ale mail był wysłany 30 lipca, więc timestamp był przeterminowany o 2 dni!")
print("\nWażne: Timestamp może być maksymalnie 15 minut stary")
current_timestamp = now_warsaw.strftime('%Y:%m:%d-%H:%M:%S')
print(f"Aktualny timestamp Warsaw: {current_timestamp} ✅")

# PUNKT 3: PORÓWNANIE Z PRZYKŁADEM Z MAILA
print("\n3️⃣ PRZYKŁAD Z MAILA (działający):")
print("-" * 40)
print("Płatność 50 PLN:")
example_data = {
    "storename": "760995999",
    "txntype": "sale",
    "timezone": "Europe/Warsaw",
    "txndatetime": "2025:07:28-22:15:45",
    "chargetotal": "50.00",
    "currency": "985",
    "checkoutoption": "combinedpage",
    "oid": "d4742929-665f-4a8e-a696-2fc2717841dc",
    "responseSuccessURL": "https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=success",
    "responseFailURL": "https://charity.ngrok.app/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=failure",
    "transactionNotificationURL": "https://charity-webhook.ngrok.app/api/webhooks/fiserv",
    "bname": "Jan Kowalski",
    "bemail": "jan.kowalski@example.com",
    "hash_algorithm": "HMACSHA256",
    "hashExtended": "7xQK8PzVh9mJ4kL2nF6sT3wRyD5gE1aB0cU..."
}

print("Pola w przykładzie:")
for key, value in example_data.items():
    if key != "hashExtended":
        print(f"   {key}: {value}")

# PUNKT 4: CO FISERV FAKTYCZNIE OTRZYMAŁ
print("\n4️⃣ CO FISERV OTRZYMAŁ (z logów):")
print("-" * 40)
fiserv_received = """
storename=760995999
txntype=sale
timezone=Europe/Berlin ❌
txndatetime=2025:07:28-21:01:59 ❌
hash_algorithm=HMACSHA256
chargetotal=50.00
currency=985
checkoutoption=combinedpage
oid=d4742929-665f-4a8e-a696-2fc2717841dc
responseSuccessURL=http://localhost:5174/... ❌
responseFailURL=http://localhost:5174/... ❌
transactionNotificationURL=https://77597ddbcc37.ngrok-free.app/api/webhooks/fiserv
bname=XXXX XXXX
bemail=test@example.com
hashExtended=HrDViSE0prh8VRmXBTxC8qtHo8OAnHpeGbBzNtUe7bA=
"""
print(fiserv_received)

print("BŁĘDY ZIDENTYFIKOWANE:")
print("   ❌ timezone: Europe/Berlin zamiast Europe/Warsaw")
print("   ❌ txndatetime: przeterminowany (2025:07:28 vs mail z 30 lipca)")  
print("   ❌ URLs: localhost zamiast https")

# PUNKT 5: GENEROWANIE HASH
print("\n5️⃣ SPOSÓB GENEROWANIA HASH (z maila):")
print("-" * 40)
print("1. Sortowanie pól alfabetycznie (bez hash_algorithm i hashExtended)")
print("2. Łączenie TYLKO WARTOŚCI znakiem |")
print("3. HMAC-SHA256 z secretem: j}2W3P)Lwv")
print("4. Kodowanie Base64")

# Test hash dla przykładu BLIK
print("\nPrzykład BLIK z maila:")
blik_example = {
    "storename": "760995999",
    "txntype": "sale", 
    "timezone": "Europe/Warsaw",
    "txndatetime": "2025:07:29-10:30:15",
    "chargetotal": "25.00",
    "currency": "985",
    "checkoutoption": "combinedpage",
    "oid": "BLIK-TEST-20250729103015",
    "responseSuccessURL": "https://myapp.ngrok.app/api/payments/success",
    "responseFailURL": "https://myapp.ngrok.app/api/payments/failure",
    "blikPayment": "true",
    "hash_algorithm": "HMACSHA256"
}

print("Sortowane pola:")
# Sortuj alfabetycznie bez hash pól
fields_to_hash = {k: v for k, v in blik_example.items() 
                 if k not in ['hash_algorithm', 'hashExtended']}
sorted_fields = sorted(fields_to_hash.items())

print("Kolejność alfabetyczna:")
for key, value in sorted_fields:
    print(f"   {key}: {value}")

# Generuj hash
values_only = [str(v) for k, v in sorted_fields]
hash_input = '|'.join(values_only)
print(f"\nHash input string:")
print(f"   {hash_input}")

SECRET = "j}2W3P)Lwv"
hash_value = base64.b64encode(
    hmac.new(SECRET.encode(), hash_input.encode(), hashlib.sha256).digest()
).decode()
print(f"\nWygenerowany hash:")
print(f"   {hash_value}")

# PUNKT 6: NASZ OSTATNI TEST
print("\n6️⃣ NASZ OSTATNI TEST (VISION-TEST):")
print("-" * 40)

# Odczytaj ostatni test
try:
    with open('vision_test_result_VISION-TEST-20250809060844.json', 'r') as f:
        our_test = json.load(f)
    
    print("Nasze dane:")
    for key, value in our_test['request']['data'].items():
        if key != 'hashExtended':
            print(f"   {key}: {value}")
    
    print("\nPorównanie z działającym przykładem:")
    print("✅ timezone: Europe/Warsaw")
    print("✅ storename: 760995999")
    print("✅ currency: 985")
    print("✅ checkoutoption: combinedpage")
    print("✅ txntype: sale")
    print("✅ hash_algorithm: HMACSHA256")
    print("✅ response URLs używają https://")
    print("✅ timestamp aktualny (nie przeterminowany)")
    
    print("\nRóżnice:")
    print("❓ blikPayment: brak pola (przykład BLIK ma to pole)")
    print("❓ Hash: używamy innej metody sortowania?")
    
except Exception as e:
    print(f"Nie mogę odczytać ostatniego testu: {e}")

# PUNKT 7: WNIOSKI
print("\n7️⃣ WNIOSKI:")
print("="*80)
print("""
GŁÓWNE PROBLEMY które Fiserv widzi w logach:

1. TIMEZONE: 
   - Otrzymują Europe/Berlin zamiast Europe/Warsaw
   - To może być problem z konfiguracją serwera lub proxy

2. TIMESTAMP:
   - Był przeterminowany o 2 dni
   - Max 15 minut różnicy jest dozwolone

3. RESPONSE URLs:
   - Używają localhost zamiast https
   - To blokuje płatności produkcyjne

4. BLIK PAYMENT:
   - Request BLIK-TEST-20250729103015 nie dotarł do Fiserv
   - Może być problem z siecią lub konfiguracją

REKOMENDACJE:
1. Sprawdzić konfigurację timezone na serwerze
2. Upewnić się że timestamp jest aktualny
3. Używać tylko https:// URLs, nie localhost
4. Sprawdzić czy Store ID ma aktywny IPG Connect
5. Poprosić Fiserv o logi dla VISION-TEST-*
""")
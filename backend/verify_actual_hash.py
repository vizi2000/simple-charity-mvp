#!/usr/bin/env python3
"""
Weryfikacja rzeczywistego hasha który otrzymał Fiserv
"""

import hmac
import hashlib
import base64
from collections import OrderedDict

def verify_fiserv_hash():
    """Sprawdź hash z rzeczywistymi danymi które otrzymał Fiserv"""
    
    print("="*70)
    print("WERYFIKACJA HASHA KTÓRY OTRZYMAŁ FISERV")
    print("="*70)
    
    # DOKŁADNE dane które otrzymał Fiserv (z logów)
    received_fields = OrderedDict([
        ('storename', '760995999'),
        ('txntype', 'sale'),
        ('timezone', 'Europe/Berlin'),  # ❌ Błędne!
        ('txndatetime', '2025:07:28-21:01:59'),  # ❌ UTC zamiast Warsaw!
        ('hash_algorithm', 'HMACSHA256'),
        ('chargetotal', '50.00'),
        ('currency', '985'),
        ('checkoutoption', 'combinedpage'),
        ('oid', 'd4742929-665f-4a8e-a696-2fc2717841dc'),
        ('responseSuccessURL', 'http://localhost:5174/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=success'),
        ('responseFailURL', 'http://localhost:5174/platnosc/d4742929-665f-4a8e-a696-2fc2717841dc/status?result=failure'),
        ('transactionNotificationURL', 'https://77597ddbcc37.ngrok-free.app/api/webhooks/fiserv'),
        ('bname', 'XXXX XXXX'),
        ('bemail', 'test@example.com'),
        ('hashExtended', 'HrDVISE0prh8VRmXBTxC8qtHo8OAnHpeGbBzNtUe7bA=')
    ])
    
    received_hash = 'HrDVISE0prh8VRmXBTxC8qtHo8OAnHpeGbBzNtUe7bA='
    
    print("\n📋 DANE OTRZYMANE PRZEZ FISERV:")
    print("-" * 50)
    for key, value in received_fields.items():
        if key == 'hashExtended':
            print(f"{key:30} = {value[:20]}...")
        else:
            print(f"{key:30} = {value}")
    
    print("\n⚠️ PROBLEMY:")
    print(f"  1. Timezone: Europe/Berlin (powinno być Europe/Warsaw)")
    print(f"  2. Timestamp: 21:01:59 (UTC) zamiast 23:01:59 (Warsaw)")
    print(f"  3. Wysłane o 23:02:09 Warsaw, ale timestamp mówi 21:01:59")
    print(f"  4. Różnica 2 GODZINY - timestamp PRZETERMINOWANY!")
    
    # Pola do hasha (bez hash_algorithm i hashExtended)
    fields_for_hash = OrderedDict()
    for key, value in received_fields.items():
        if key not in ['hash_algorithm', 'hashExtended']:
            fields_for_hash[key] = value
    
    # Sortuj alfabetycznie
    sorted_fields = OrderedDict(sorted(fields_for_hash.items()))
    
    print("\n📝 POLA DO HASHA (posortowane alfabetycznie):")
    for i, (key, value) in enumerate(sorted_fields.items(), 1):
        print(f"  {i:2}. {key}: {value[:50]}...")
    
    # String do hasha
    hash_string = '|'.join(str(v) for v in sorted_fields.values())
    
    print(f"\n🔗 STRING DO HASHA:")
    print(f"{hash_string[:200]}...")
    print(f"...{hash_string[-100:]}")
    
    # Test z różnymi secretami
    secrets = [
        ("j}2W3P)Lwv", "Oryginalny"),
        ("c7dP/$5PBx", "Alternatywny"),
        ("aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG", "REST API")
    ]
    
    print("\n🔑 TEST Z RÓŻNYMI SECRETAMI:")
    print("-" * 50)
    
    for secret, name in secrets:
        hash_bytes = hmac.new(
            secret.encode('utf-8'),
            hash_string.encode('utf-8'),
            hashlib.sha256
        ).digest()
        calculated_hash = base64.b64encode(hash_bytes).decode('utf-8')
        
        if calculated_hash == received_hash:
            print(f"✅ ZNALEZIONO! Secret: {name} ({secret})")
            print(f"   Hash: {calculated_hash}")
            return secret
        else:
            print(f"❌ {name:15} -> {calculated_hash[:20]}... (nie pasuje)")
    
    print("\n" + "="*70)
    print("ANALIZA CZASU:")
    print("="*70)
    
    print("""
📅 28 lipca 2025:
   23:02:09 Warsaw = Czas wysłania requestu
   21:02:09 UTC     = Ten sam moment w UTC
   21:01:59         = Timestamp w formularzu (10 sekund wcześniej?)
   
❌ BŁĄD: Wysłano timestamp UTC zamiast Warsaw!
   
Powinno być:
   23:01:59 Warsaw (lub 23:02:09 jeśli aktualny)
   
Fiserv sprawdza czy timestamp jest aktualny (max 5-10 minut różnicy).
Timestamp 21:01:59 był PRZETERMINOWANY o 2 godziny!
    """)
    
    print("\n" + "="*70)
    print("ROZWIĄZANIE:")
    print("="*70)
    
    print("""
✅ CO NAPRAWIĆ:
1. Zawsze używaj datetime.now(ZoneInfo('Europe/Warsaw'))
2. NIGDY nie używaj datetime.utcnow()
3. Timezone MUSI być 'Europe/Warsaw'
4. Timestamp musi być aktualny czas warszawski

❌ BŁĘDNY KOD (prawdopodobnie był):
   txndatetime = datetime.utcnow().strftime("%Y:%m:%d-%H:%M:%S")
   timezone = 'Europe/Berlin'

✅ POPRAWNY KOD:
   warsaw_tz = ZoneInfo('Europe/Warsaw')
   txndatetime = datetime.now(warsaw_tz).strftime("%Y:%m:%d-%H:%M:%S")
   timezone = 'Europe/Warsaw'
    """)

if __name__ == "__main__":
    verify_fiserv_hash()
#!/usr/bin/env python3
"""
Debug błędu walidacji Fiserv - sprawdź wszystkie pola
"""

import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.fiserv_ipg_client import FiservIPGClient

def debug_validation():
    """Sprawdź dokładnie co wysyłamy do Fiserv"""
    
    print("="*60)
    print("DEBUG: BŁĄD WALIDACJI FISERV")
    print("="*60)
    
    client = FiservIPGClient()
    
    # Generuj dane testowe
    test_order_id = f"DEBUG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    form_data = client.create_payment_form_data(
        amount=10.00,
        order_id=test_order_id,
        description="Debug validation error",
        success_url="https://charity.ngrok.app/success",
        failure_url="https://charity.ngrok.app/failure",
        notification_url="https://charity-webhook.ngrok.app/webhook",
        customer_info={
            "name": "Jan Kowalski",
            "email": "jan@example.com"
        }
    )
    
    fields = form_data['form_fields']
    
    print("\n📋 WSZYSTKIE WYSYŁANE POLA:")
    print("-" * 40)
    
    # Sortuj alfabetycznie dla lepszej czytelności
    for key in sorted(fields.keys()):
        value = fields[key]
        if key == 'hashExtended':
            print(f"{key:30} = {value[:20]}... (len: {len(value)})")
        else:
            print(f"{key:30} = {value}")
    
    print("\n🔍 ANALIZA KLUCZOWYCH PÓL:")
    print("-" * 40)
    
    # Sprawdź timezone
    timezone = fields.get('timezone')
    print(f"\n1. TIMEZONE: {timezone}")
    if timezone != 'Europe/Warsaw':
        print(f"   ❌ BŁĄD! Powinno być 'Europe/Warsaw'")
    else:
        print(f"   ✅ OK")
    
    # Sprawdź timestamp
    txndatetime = fields.get('txndatetime')
    print(f"\n2. TIMESTAMP: {txndatetime}")
    
    # Weryfikuj format
    if len(txndatetime) != 19:
        print(f"   ❌ BŁĄD! Nieprawidłowa długość: {len(txndatetime)}")
    elif txndatetime[4] != ':' or txndatetime[7] != ':' or txndatetime[10] != '-':
        print(f"   ❌ BŁĄD! Nieprawidłowy format")
    else:
        print(f"   ✅ Format OK")
    
    # Sprawdź aktualność
    warsaw_tz = ZoneInfo('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    
    try:
        parts = txndatetime.split('-')
        date_parts = parts[0].split(':')
        time_parts = parts[1].split(':')
        
        ts_dt = datetime(
            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
            int(time_parts[0]), int(time_parts[1]), int(time_parts[2]),
            tzinfo=warsaw_tz
        )
        
        diff = (now - ts_dt).total_seconds()
        
        if abs(diff) < 60:
            print(f"   ✅ Czas aktualny (różnica {abs(diff):.1f}s)")
        elif diff > 0:
            print(f"   ⚠️ Timestamp z przeszłości ({diff:.0f}s temu)")
        else:
            print(f"   ❌ Timestamp z przyszłości! ({abs(diff):.0f}s)")
            
    except Exception as e:
        print(f"   ❌ Błąd parsowania: {e}")
    
    # Sprawdź wymagane pola
    print("\n3. WYMAGANE POLA:")
    required_fields = [
        'storename',
        'txntype', 
        'timezone',
        'txndatetime',
        'hash_algorithm',
        'chargetotal',
        'currency',
        'checkoutoption',
        'oid'
    ]
    
    missing = []
    for field in required_fields:
        if field not in fields or not fields[field]:
            missing.append(field)
            print(f"   ❌ {field}: BRAK!")
        else:
            print(f"   ✅ {field}: {fields[field]}")
    
    # Sprawdź URLs
    print("\n4. ADRESY URL:")
    url_fields = ['responseSuccessURL', 'responseFailURL', 'transactionNotificationURL']
    for field in url_fields:
        url = fields.get(field)
        if url:
            if url.startswith('http://localhost'):
                print(f"   ⚠️ {field}: localhost (Fiserv nie może dotrzeć)")
            elif url.startswith('https://'):
                print(f"   ✅ {field}: OK")
            else:
                print(f"   ❌ {field}: Nieprawidłowy protokół")
        else:
            print(f"   ⚠️ {field}: Brak (opcjonalne)")
    
    # Sprawdź hash
    print("\n5. HASH:")
    hash_alg = fields.get('hash_algorithm')
    hash_ext = fields.get('hashExtended')
    
    if hash_alg != 'HMACSHA256':
        print(f"   ❌ hash_algorithm: {hash_alg} (powinno być HMACSHA256)")
    else:
        print(f"   ✅ hash_algorithm: {hash_alg}")
    
    if not hash_ext:
        print(f"   ❌ hashExtended: BRAK!")
    elif len(hash_ext) < 20:
        print(f"   ❌ hashExtended: Za krótki ({len(hash_ext)} znaków)")
    else:
        print(f"   ✅ hashExtended: OK (długość: {len(hash_ext)})")
    
    # Oblicz hash ponownie do weryfikacji
    print("\n6. WERYFIKACJA HASHA:")
    exclude_fields = {'hash', 'hashExtended', 'hash_algorithm'}
    hash_fields = {k: v for k, v in fields.items() if k not in exclude_fields}
    sorted_fields = sorted(hash_fields.items())
    hash_string = '|'.join(str(v) for k, v in sorted_fields)
    
    print(f"   String do hasha (pierwsze 150 znaków):")
    print(f"   {hash_string[:150]}...")
    
    # Podsumowanie
    print("\n" + "="*60)
    print("PODSUMOWANIE:")
    print("="*60)
    
    if missing:
        print("❌ BRAKUJĄCE POLA:")
        for field in missing:
            print(f"   - {field}")
    
    problems = []
    
    if timezone != 'Europe/Warsaw':
        problems.append(f"Timezone: {timezone} (powinno być Europe/Warsaw)")
    
    if abs(diff) > 300:  # Więcej niż 5 minut
        problems.append(f"Timestamp nieaktualny (różnica {abs(diff)/60:.1f} minut)")
    
    if problems:
        print("\n❌ ZNALEZIONE PROBLEMY:")
        for problem in problems:
            print(f"   - {problem}")
    else:
        print("\n✅ Wszystkie pola wyglądają poprawnie")
        print("\n🤔 Możliwe przyczyny błędu walidacji:")
        print("   1. Konto/sklep nie jest poprawnie skonfigurowany")
        print("   2. Brak uprawnień do Combined Page")
        print("   3. Nieprawidłowy shared secret do generowania hasha")
        print("   4. URLs mogą być blokowane przez Fiserv")
    
    return fields

if __name__ == "__main__":
    debug_validation()
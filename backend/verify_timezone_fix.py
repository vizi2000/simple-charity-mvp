#!/usr/bin/env python3
"""
Weryfikacja poprawki timezone i timestamp dla Fiserv
"""

import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# Dodaj ścieżkę do modułów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.fiserv_ipg_client import FiservIPGClient

def verify_fix():
    """Weryfikuj że timezone i timestamp są poprawne"""
    
    print("="*60)
    print("WERYFIKACJA POPRAWKI TIMEZONE/TIMESTAMP")
    print("="*60)
    
    # Inicjalizuj klienta
    client = FiservIPGClient()
    
    # Wygeneruj dane formularza
    test_data = client.create_payment_form_data(
        amount=50.00,
        order_id="VERIFY-FIX-TEST",
        description="Test poprawki",
        success_url="https://charity.ngrok.app/success",
        failure_url="https://charity.ngrok.app/failure",
        notification_url="https://charity-webhook.ngrok.app/webhook",
        customer_info={
            "name": "Test User",
            "email": "test@example.com"
        }
    )
    
    fields = test_data['form_fields']
    
    print("\n✅ SPRAWDZENIE POPRAWEK:")
    print("-" * 40)
    
    # 1. Sprawdź timezone
    timezone = fields.get('timezone')
    print(f"1. Timezone: {timezone}")
    if timezone == 'Europe/Warsaw':
        print("   ✅ POPRAWNE - Europe/Warsaw")
    else:
        print(f"   ❌ BŁĄD - powinno być Europe/Warsaw, jest {timezone}")
    
    # 2. Sprawdź timestamp
    txndatetime = fields.get('txndatetime')
    print(f"\n2. Timestamp: {txndatetime}")
    
    # Porównaj z aktualnym czasem warszawskim
    warsaw_tz = ZoneInfo('Europe/Warsaw')
    now_warsaw = datetime.now(warsaw_tz)
    expected = now_warsaw.strftime("%Y:%m:%d-%H:%M:%S")
    
    print(f"   Oczekiwany (aktualny Warsaw): {expected}")
    
    # Parsuj timestamp z formularza
    try:
        parts = txndatetime.split('-')
        date_parts = parts[0].split(':')
        time_parts = parts[1].split(':')
        
        form_dt = datetime(
            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
            int(time_parts[0]), int(time_parts[1]), int(time_parts[2]),
            tzinfo=warsaw_tz
        )
        
        diff = abs((now_warsaw - form_dt).total_seconds())
        
        if diff < 5:  # Mniej niż 5 sekund różnicy
            print(f"   ✅ POPRAWNE - timestamp warszawski (różnica {diff:.1f}s)")
        else:
            hours_diff = diff / 3600
            print(f"   ❌ BŁĄD - różnica {hours_diff:.1f} godzin!")
            if abs(hours_diff - 2) < 0.1:
                print("   ⚠️  Wygląda na to że wysyłasz czas UTC zamiast Warsaw!")
    except Exception as e:
        print(f"   ❌ Błąd parsowania: {e}")
    
    # 3. Sprawdź hash string
    print(f"\n3. Hash string:")
    exclude_fields = {'hash', 'hashExtended', 'hash_algorithm'}
    hash_fields = {k: v for k, v in fields.items() if k not in exclude_fields}
    sorted_fields = sorted(hash_fields.items())
    hash_string = '|'.join(str(v) for k, v in sorted_fields)
    
    print(f"   Pierwsze 100 znaków: {hash_string[:100]}...")
    
    if 'Europe/Warsaw' in hash_string:
        print("   ✅ Zawiera Europe/Warsaw")
    else:
        print("   ❌ NIE zawiera Europe/Warsaw!")
    
    if txndatetime in hash_string:
        print(f"   ✅ Zawiera timestamp {txndatetime}")
    else:
        print("   ❌ NIE zawiera timestampa!")
    
    # 4. Pokaż wszystkie pola
    print("\n4. WSZYSTKIE POLA FORMULARZA:")
    print("-" * 40)
    for key in ['storename', 'txntype', 'timezone', 'txndatetime', 'chargetotal', 
                'currency', 'checkoutoption', 'oid']:
        if key in fields:
            print(f"   {key}: {fields[key]}")
    
    print("\n" + "="*60)
    print("PODSUMOWANIE:")
    print("="*60)
    
    if timezone == 'Europe/Warsaw' and diff < 5:
        print("✅ POPRAWKA DZIAŁA PRAWIDŁOWO!")
        print("   - Timezone: Europe/Warsaw")
        print("   - Timestamp: Aktualny czas warszawski")
        print("\n🎉 Możesz teraz przetestować płatności z Fiserv")
    else:
        print("❌ NADAL SĄ PROBLEMY!")
        if timezone != 'Europe/Warsaw':
            print(f"   - Timezone jest {timezone} zamiast Europe/Warsaw")
        if diff >= 5:
            print(f"   - Timestamp ma różnicę {diff/3600:.1f} godzin")
        print("\n🔧 Sprawdź czy:")
        print("   1. Zapisałeś zmiany w fiserv_ipg_client.py")
        print("   2. Zrestartowałeś aplikację")
        print("   3. Nie ma innych plików nadpisujących te wartości")

if __name__ == "__main__":
    verify_fix()
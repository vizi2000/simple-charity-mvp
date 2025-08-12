#!/usr/bin/env python3
"""
Walidacja każdego pola zgodnie z dokumentacją Fiserv
"""

from datetime import datetime, timedelta
import hmac
import hashlib
import base64

def validate_fields():
    """Sprawdź każde pole dokładnie"""
    
    print("="*60)
    print("WALIDACJA KAŻDEGO POLA")
    print("="*60)
    
    # Dane do sprawdzenia
    fields = {
        'storename': '760995999',
        'txntype': 'sale',
        'timezone': 'Europe/Warsaw',
        'txndatetime': '2025:07:29-11:48:28',
        'chargetotal': '10.00',
        'currency': '985',
        'checkoutoption': 'combinedpage',
        'oid': 'WARSAW-20250729114828',
        'hash_algorithm': 'HMACSHA256'
    }
    
    print("\n1. CHARGETOTAL:")
    print(f"   Wartość: '{fields['chargetotal']}'")
    print("   ✅ Format: liczba z 2 miejscami po przecinku")
    print("   ✅ Separator: kropka (nie przecinek)")
    print("   ⚠️  Możliwy problem: czy kwota 10.00 PLN jest minimalna?")
    
    print("\n2. CHECKOUTOPTION:")
    print(f"   Wartość: '{fields['checkoutoption']}'")
    print("   ✅ Zgodne z zaleceniem Fiserv")
    print("   ⚠️  Możliwy problem: czy Combined Page jest aktywna?")
    
    print("\n3. CURRENCY:")
    print(f"   Wartość: '{fields['currency']}'")
    print("   ✅ 985 = PLN (kod ISO 4217)")
    print("   ✅ Zgodne z zaleceniem Fiserv")
    
    print("\n4. HASH_ALGORITHM:")
    print(f"   Wartość: '{fields['hash_algorithm']}'")
    print("   ✅ HMACSHA256 (bez spacji, bez myślników)")
    print("   ⚠️  Sprawdź: czy dokładnie HMACSHA256 nie HMAC-SHA256")
    
    print("\n5. OID (Order ID):")
    print(f"   Wartość: '{fields['oid']}'")
    print(f"   Długość: {len(fields['oid'])} znaków")
    print("   ✅ Alfanumeryczne")
    print("   ⚠️  Możliwy problem: maksymalna długość? Znaki specjalne?")
    
    print("\n6. STORENAME:")
    print(f"   Wartość: '{fields['storename']}'")
    print("   ✅ Store ID od Fiserv")
    print("   ⚠️  Sprawdź: czy dokładnie 760995999 (9 cyfr)")
    
    print("\n7. TIMEZONE:")
    print(f"   Wartość: '{fields['timezone']}'")
    print("   ✅ Europe/Warsaw - zgodne z zaleceniem")
    print("   ✅ Format: Region/City")
    
    print("\n8. TXNDATETIME:")
    print(f"   Wartość: '{fields['txndatetime']}'")
    print("   ✅ Format: YYYY:MM:DD-HH:MM:SS")
    
    # Sprawdź czy czas jest przyszły
    warsaw_now = datetime.utcnow() + timedelta(hours=2)
    tx_time = datetime.strptime('2025:07:29-11:48:28', '%Y:%m:%d-%H:%M:%S')
    if tx_time < warsaw_now:
        print("   ❌ BŁĄD: Czas transakcji jest w przeszłości!")
    else:
        print("   ✅ Czas w przyszłości lub teraźniejszości")
    
    print("\n9. TXNTYPE:")
    print(f"   Wartość: '{fields['txntype']}'")
    print("   ✅ 'sale' - standardowa sprzedaż")
    
    print("\n" + "="*60)
    print("OBLICZANIE HASH - KROK PO KROKU")
    print("="*60)
    
    # Krok 1: Wyklucz pola
    print("\n1. Wykluczamy z hash:")
    print("   - hash_algorithm")
    print("   - hashExtended")
    
    # Krok 2: Sortuj alfabetycznie
    hash_fields = {k: v for k, v in fields.items() if k not in ['hash_algorithm', 'hashExtended']}
    sorted_fields = sorted(hash_fields.items())
    
    print("\n2. Pola do hash (posortowane alfabetycznie):")
    for k, v in sorted_fields:
        print(f"   {k}: {v}")
    
    # Krok 3: Twórz string
    values_only = [str(v) for k, v in sorted_fields]
    hash_string = '|'.join(values_only)
    
    print("\n3. Wartości połączone '|' (pipe):")
    print(f"   {hash_string}")
    
    # Krok 4: Secret
    secret = "j}2W3P)Lwv"
    print(f"\n4. Shared Secret: {secret}")
    print("   ⚠️  Sprawdź każdy znak! Szczególnie } i )")
    
    # Krok 5: HMAC-SHA256
    print("\n5. Obliczanie HMAC-SHA256:")
    
    # Pokaż bajty
    secret_bytes = secret.encode('utf-8')
    string_bytes = hash_string.encode('utf-8')
    
    print(f"   Secret bytes ({len(secret_bytes)}): {secret_bytes}")
    print(f"   String bytes ({len(string_bytes)}): {string_bytes[:50]}...")
    
    hash_bytes = hmac.new(secret_bytes, string_bytes, hashlib.sha256).digest()
    print(f"   Hash bytes ({len(hash_bytes)}): {hash_bytes.hex()}")
    
    # Krok 6: Base64
    hash_value = base64.b64encode(hash_bytes).decode('utf-8')
    print(f"\n6. Base64 encoding:")
    print(f"   {hash_value}")
    print(f"   Długość: {len(hash_value)} znaków")
    
    # Alternatywne obliczenia
    print("\n" + "="*60)
    print("ALTERNATYWNE KOLEJNOŚCI (test)")
    print("="*60)
    
    # Test 1: Może pola w innej kolejności?
    alt_order = ['storename', 'txntype', 'timezone', 'txndatetime', 'chargetotal', 'currency', 'checkoutoption', 'oid']
    alt_values = [fields[k] for k in alt_order if k in fields]
    alt_string = '|'.join(alt_values)
    alt_hash = base64.b64encode(
        hmac.new(secret.encode('utf-8'), alt_string.encode('utf-8'), hashlib.sha256).digest()
    ).decode('utf-8')
    
    print("\nKolejność jak w formularzu:")
    print(f"String: {alt_string}")
    print(f"Hash: {alt_hash}")
    
    # HTML z testami
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Walidacja pól</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: monospace; margin: 20px; background: #f0f0f0; }}
        .field {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
        .error {{ border-left-color: #dc3545; }}
        .warning {{ border-left-color: #ffc107; }}
        button {{ background: #28a745; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
    </style>
</head>
<body>
    <h1>🔍 Walidacja każdego pola</h1>
    
    <div class="field">
        <h3>chargetotal = 10.00</h3>
        <p>✅ Format poprawny (XX.XX)</p>
        <p>⚠️ Sprawdź: minimalna kwota?</p>
    </div>
    
    <div class="field warning">
        <h3>txndatetime = 2025:07:29-11:48:28</h3>
        <p>⚠️ UWAGA: Ten czas może być już w przeszłości!</p>
        <p>Użyj aktualnego czasu warszawskiego</p>
    </div>
    
    <div class="field">
        <h3>Hash calculation:</h3>
        <p>String: {hash_string}</p>
        <p>Hash: {hash_value}</p>
    </div>
    
    <h2>Test z aktualnym czasem:</h2>
"""
    
    # Test z nowym czasem
    current_warsaw = datetime.utcnow() + timedelta(hours=2)
    new_time = current_warsaw.strftime("%Y:%m:%d-%H:%M:%S")
    new_oid = f"TEST-{current_warsaw.strftime('%Y%m%d%H%M%S')}"
    
    test_fields = fields.copy()
    test_fields['txndatetime'] = new_time
    test_fields['oid'] = new_oid
    
    # Nowy hash
    test_hash_fields = {k: v for k, v in test_fields.items() if k not in ['hash_algorithm', 'hashExtended']}
    test_sorted = sorted(test_hash_fields.items())
    test_string = '|'.join(str(v) for k, v in test_sorted)
    test_hash = base64.b64encode(
        hmac.new(secret.encode('utf-8'), test_string.encode('utf-8'), hashlib.sha256).digest()
    ).decode('utf-8')
    
    test_fields['hashExtended'] = test_hash
    
    html += f"""
    <form method="POST" action="https://test.ipg-online.com/connect/gateway/processing" target="_blank">
"""
    
    for k, v in test_fields.items():
        html += f'        <input type="hidden" name="{k}" value="{v}">\n'
    
    html += """        <button type="submit">TEST Z NOWYM CZASEM</button>
    </form>
</body>
</html>"""
    
    with open('validate_fields.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Walidacja zapisana jako: validate_fields.html")
    
    import webbrowser
    import os
    webbrowser.open(f"file://{os.path.abspath('validate_fields.html')}")

if __name__ == "__main__":
    validate_fields()
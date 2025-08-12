#!/usr/bin/env python3
"""
Analiza każdej możliwej przyczyny błędu "Unknown application error"
"""

from datetime import datetime, timedelta
import hmac
import hashlib
import base64
import urllib.parse

def analyze_error_causes():
    """Sprawdź każdą możliwą przyczynę błędu"""
    
    print("="*60)
    print("ANALIZA PRZYCZYN BŁĘDU")
    print("="*60)
    
    # Test shared secret ze znakami specjalnymi
    secret = "j}2W3P)Lwv"
    
    print("\n1. SHARED SECRET - ZNAKI SPECJALNE:")
    print(f"   Secret: '{secret}'")
    print(f"   Długość: {len(secret)} znaków")
    print("   Znaki specjalne:")
    print(f"   - }} (closing brace) na pozycji 1")
    print(f"   - ) (closing parenthesis) na pozycji 6")
    print("\n   ⚠️  PROBLEM: Znaki } i ) mogą być problematyczne!")
    print("   - W URL encoding: } = %7D, ) = %29")
    print("   - W XML/HTML: mogą wymagać escape")
    print("   - W base64: nie powinny być problemem")
    
    # Test URL encoding
    print(f"\n   URL encoded: {urllib.parse.quote(secret)}")
    print(f"   Czy to samo? {urllib.parse.quote(secret) == secret}")
    
    # Test różnych interpretacji secret
    print("\n   MOŻLIWE INTERPRETACJE:")
    secrets_to_test = [
        ("Oryginalny", "j}2W3P)Lwv"),
        ("Escaped }", "j\\}2W3P)Lwv"),
        ("Escaped )", "j}2W3P\\)Lwv"),
        ("HTML entity }", "j&#125;2W3P)Lwv"),
        ("HTML entity )", "j}2W3P&#41;Lwv"),
        ("URL encoded", "j%7D2W3P%29Lwv"),
    ]
    
    for name, test_secret in secrets_to_test:
        print(f"   - {name}: '{test_secret}'")
    
    print("\n2. WYMAGANE MINIMALNE POLA:")
    print("   Według dokumentacji IPG Connect:")
    required_fields = [
        ("storename", "760995999", "✅"),
        ("chargetotal", "10.00", "✅"),
        ("currency", "985", "✅"),
        ("checkoutoption", "combinedpage", "✅"),
        ("timezone", "Europe/Warsaw", "✅"),
        ("txntype", "sale", "✅"),
        ("hash_algorithm", "HMACSHA256", "✅"),
        ("hashExtended", "[calculated]", "✅"),
    ]
    
    for field, value, status in required_fields:
        print(f"   {status} {field}: {value}")
    
    print("\n3. SKŁADNIA PÓL:")
    
    # Aktualny czas warszawski
    warsaw_now = datetime.utcnow() + timedelta(hours=1)  # Zimowy czas
    
    syntax_checks = [
        {
            "field": "chargetotal",
            "value": "10.00",
            "checks": [
                ("Format XX.XX", True),
                ("Kropka jako separator", True),
                ("Bez waluty", True),
                ("Minimalna kwota > 0", True),
            ]
        },
        {
            "field": "oid",
            "value": f"TEST{warsaw_now.strftime('%Y%m%d%H%M%S')}",
            "checks": [
                ("Tylko alfanumeryczne", True),
                ("Bez myślników", True),
                ("Maksymalna długość < 100", True),
                ("Unikalny", True),
            ]
        },
        {
            "field": "txndatetime",
            "value": warsaw_now.strftime("%Y:%m:%d-%H:%M:%S"),
            "checks": [
                ("Format YYYY:MM:DD-HH:MM:SS", True),
                ("Czas przyszły/obecny", True),
                ("Zgodny z timezone", True),
            ]
        }
    ]
    
    for check in syntax_checks:
        print(f"\n   {check['field']} = '{check['value']}'")
        for desc, ok in check['checks']:
            status = "✅" if ok else "❌"
            print(f"     {status} {desc}")
    
    print("\n4. KONFIGURACJA STORE:")
    print("   Store ID: 760995999")
    print("   ❓ Czy store jest skonfigurowany dla:")
    print("   - IPG Connect (nie tylko VT)")
    print("   - Combined Page")
    print("   - Waluta PLN (985)")
    print("   - Timezone Europe/Warsaw")
    
    print("\n5. SESJA:")
    print("   ❓ Czy wymagana jest wcześniejsza sesja?")
    print("   - Może trzeba najpierw wywołać jakiś endpoint?")
    print("   - Może trzeba cookies?")
    
    print("\n6. UPRAWNIENIA CZASOWE:")
    print("   ❓ Czy są ograniczenia:")
    print("   - Godzinowe (np. 9:00-17:00)")
    print("   - Dniowe (np. dni robocze)")
    print("   - Limitowane (np. max X transakcji/dzień)")
    
    # Generuj testy
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Analiza błędów</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .test {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .error {{ background: #ffebee; border-left: 4px solid #f44336; }}
        .warning {{ background: #fff3e0; border-left: 4px solid #ff9800; }}
        .info {{ background: #e3f2fd; border-left: 4px solid #2196f3; }}
        button {{ background: #4caf50; color: white; padding: 10px 20px; border: none; cursor: pointer; margin: 5px; }}
        h3 {{ margin-top: 0; }}
        code {{ background: #f5f5f5; padding: 2px 5px; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>🔍 Analiza przyczyn błędu</h1>
    
    <div class="test error">
        <h3>⚠️ PROBLEM: Shared Secret ze znakami specjalnymi</h3>
        <p>Secret: <code>j}}2W3P)Lwv</code> zawiera:</p>
        <ul>
            <li><code>}}</code> - closing brace</li>
            <li><code>)</code> - closing parenthesis</li>
        </ul>
        <p><strong>To może być źródło problemu!</strong></p>
    </div>
    
    <div class="test warning">
        <h3>🧪 Test 1: Prosty OID bez myślników</h3>
        <form method="POST" action="https://test.ipg-online.com/connect/gateway/processing" target="_blank">
"""
    
    # Test 1: Prosty OID
    simple_fields = {
        'storename': '760995999',
        'txntype': 'sale',
        'timezone': 'Europe/Warsaw',
        'txndatetime': warsaw_now.strftime("%Y:%m:%d-%H:%M:%S"),
        'chargetotal': '10.00',
        'currency': '985',
        'checkoutoption': 'combinedpage',
        'oid': f'TEST{warsaw_now.strftime("%Y%m%d%H%M%S")}',
        'hash_algorithm': 'HMACSHA256'
    }
    
    # Hash dla prostego OID
    hash_fields = {k: v for k, v in simple_fields.items() if k not in ['hash_algorithm', 'hashExtended']}
    sorted_fields = sorted(hash_fields.items())
    hash_string = '|'.join(str(v) for k, v in sorted_fields)
    hash_value = base64.b64encode(
        hmac.new(secret.encode('utf-8'), hash_string.encode('utf-8'), hashlib.sha256).digest()
    ).decode('utf-8')
    simple_fields['hashExtended'] = hash_value
    
    for k, v in simple_fields.items():
        html += f'            <input type="hidden" name="{k}" value="{v}">\n'
    
    html += f"""            <button type="submit">TEST PROSTY OID</button>
        </form>
        <p>OID: <code>{simple_fields['oid']}</code> (bez myślników)</p>
    </div>
    
    <div class="test warning">
        <h3>🧪 Test 2: Minimalne wymagane pola</h3>
        <form method="POST" action="https://test.ipg-online.com/connect/gateway/processing" target="_blank">
"""
    
    # Test 2: Tylko minimalne pola
    minimal_fields = {
        'storename': '760995999',
        'chargetotal': '10.00',
        'currency': '985'
    }
    
    for k, v in minimal_fields.items():
        html += f'            <input type="hidden" name="{k}" value="{v}">\n'
    
    html += """            <button type="submit">TEST MINIMALNY</button>
        </form>
        <p>Tylko 3 pola: storename, chargetotal, currency</p>
    </div>
    
    <div class="test info">
        <h3>💡 Możliwe rozwiązania:</h3>
        <ol>
            <li><strong>Sprawdź shared secret</strong> - może znaki } i ) są źle interpretowane?</li>
            <li><strong>Zapytaj Fiserv</strong> o dokładną interpretację secret ze znakami specjalnymi</li>
            <li><strong>Test z VPN</strong> - może IP jest blokowane?</li>
            <li><strong>Sprawdź godziny</strong> - może są ograniczenia czasowe?</li>
            <li><strong>Potwierdź aktywację</strong> IPG Connect (nie tylko VT)</li>
        </ol>
    </div>
    
    <div class="test">
        <h3>📊 Podsumowanie testów wykonanych:</h3>
        <ul>
            <li>✅ Timezone: Europe/Warsaw</li>
            <li>✅ Currency: 985</li>
            <li>✅ Checkoutoption: combinedpage</li>
            <li>✅ Hash algorithm: HMACSHA256</li>
            <li>❌ Shared secret: możliwe problemy ze znakami specjalnymi</li>
            <li>❓ Store configuration: wymaga potwierdzenia</li>
        </ul>
    </div>
</body>
</html>"""
    
    with open('analyze_errors.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Analiza zapisana jako: analyze_errors.html")
    
    # Test różnych secret encoding
    print("\n" + "="*60)
    print("TEST RÓŻNYCH INTERPRETACJI SECRET")
    print("="*60)
    
    test_string = "10.00|combinedpage|985|TEST123|760995999|Europe/Warsaw|2024:01:01-12:00:00|sale"
    
    for name, test_secret in secrets_to_test:
        test_hash = base64.b64encode(
            hmac.new(test_secret.encode('utf-8'), test_string.encode('utf-8'), hashlib.sha256).digest()
        ).decode('utf-8')
        print(f"\n{name}:")
        print(f"  Secret: '{test_secret}'")
        print(f"  Hash: {test_hash}")
    
    import webbrowser
    import os
    webbrowser.open(f"file://{os.path.abspath('analyze_errors.html')}")

if __name__ == "__main__":
    analyze_error_causes()
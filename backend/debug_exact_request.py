#!/usr/bin/env python3
"""
Debug dokładnego requesta zgodnie z wymaganiami Fiserv
"""

from datetime import datetime, timezone
import hmac
import hashlib
import base64

def debug_exact_request():
    """Pokaż dokładnie co wysyłamy"""
    
    print("="*60)
    print("DEBUG: DOKŁADNY REQUEST DLA FISERV")
    print("="*60)
    
    # Dokładne dane od Fiserv
    shared_secret = "j}2W3P)Lwv"
    
    # Przygotuj dane
    order_id = f"DEBUG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    txn_datetime = datetime.now(timezone.utc).strftime("%Y:%m:%d-%H:%M:%S")
    
    # Wymagane pola
    fields = {
        'storename': '760995999',
        'txntype': 'sale',
        'timezone': 'Europe/Warsaw',
        'txndatetime': txn_datetime,
        'chargetotal': '10.00',
        'currency': '985',
        'checkoutoption': 'combinedpage',
        'oid': order_id,
        'hash_algorithm': 'HMACSHA256'
    }
    
    print("\n1. POLA DO WYSŁANIA:")
    for k, v in sorted(fields.items()):
        print(f"   {k}: {v}")
    
    # Oblicz hash - DOKŁADNIE według specyfikacji
    # Wykluczamy hash_algorithm i hashExtended
    hash_fields = {k: v for k, v in fields.items() if k not in ['hash_algorithm', 'hashExtended']}
    
    # Sortuj alfabetycznie
    sorted_fields = sorted(hash_fields.items())
    
    print("\n2. POLA DO HASHA (posortowane):")
    for k, v in sorted_fields:
        print(f"   {k}: {v}")
    
    # Twórz string do hasha
    hash_string = '|'.join(str(v) for k, v in sorted_fields)
    
    print(f"\n3. STRING DO HASHA:")
    print(f"   {hash_string}")
    
    # Oblicz HMAC-SHA256
    hash_bytes = hmac.new(
        shared_secret.encode('utf-8'),
        hash_string.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Base64 encode
    hash_value = base64.b64encode(hash_bytes).decode('utf-8')
    
    print(f"\n4. OBLICZONY HASH:")
    print(f"   Secret: {shared_secret}")
    print(f"   Algorithm: HMAC-SHA256")
    print(f"   Base64: {hash_value}")
    
    # Dodaj hash do pól
    fields['hashExtended'] = hash_value
    
    # Generuj curl command
    print("\n5. CURL COMMAND:")
    curl_data = '&'.join([f"{k}={v}" for k, v in fields.items()])
    print(f"""
curl -X POST 'https://test.ipg-online.com/connect/gateway/processing' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d '{curl_data}'
""")
    
    # HTML test
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Debug Request Fiserv</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: monospace; max-width: 1200px; margin: 20px auto; padding: 20px; }}
        .section {{ background: #f0f0f0; padding: 20px; margin: 20px 0; }}
        .field {{ background: white; padding: 5px 10px; margin: 5px 0; }}
        button {{ background: #007bff; color: white; padding: 15px 30px; border: none; cursor: pointer; font-size: 16px; }}
        .error {{ color: red; font-weight: bold; }}
        .success {{ color: green; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Debug: Dokładny Request dla Fiserv</h1>
    
    <div class="section">
        <h2>✅ Wymagania od Fiserv Support:</h2>
        <div class="field">shared secret = <span class="success">j}}2W3P)Lwv</span></div>
        <div class="field">timezone = <span class="success">Europe/Warsaw</span></div>
        <div class="field">currency = <span class="success">985</span></div>
        <div class="field">checkoutoption = <span class="success">combinedpage</span></div>
    </div>
    
    <div class="section">
        <h2>📝 Wysyłane pola:</h2>
"""
    
    for k, v in sorted(fields.items()):
        html += f'        <div class="field">{k} = {v}</div>\n'
    
    html += f"""    </div>
    
    <div class="section">
        <h2>🔐 Hash calculation:</h2>
        <div class="field">String: {hash_string[:100]}...</div>
        <div class="field">Secret: j}}2W3P)Lwv</div>
        <div class="field">Result: {hash_value}</div>
    </div>
    
    <div class="section">
        <h2>🚀 Test Form:</h2>
        <form method="POST" action="https://test.ipg-online.com/connect/gateway/processing" target="_blank">
"""
    
    for k, v in fields.items():
        html += f'            <input type="hidden" name="{k}" value="{v}">\n'
    
    html += """            <button type="submit">WYŚLIJ DO FISERV</button>
        </form>
    </div>
    
    <div class="section">
        <h2>⚠️ Jeśli nadal nie działa:</h2>
        <ol>
            <li>Sprawdź czy Store ID 760995999 jest aktywne dla IPG Connect</li>
            <li>Może być problem z sesją/IP - spróbuj z innego urządzenia</li>
            <li>Sprawdź w Virtual Terminal czy Combined Page jest włączona</li>
            <li>Możliwy problem z formatem daty/czasu dla strefy Warsaw</li>
        </ol>
    </div>
</body>
</html>"""
    
    with open('debug_exact_request.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Test zapisany jako: debug_exact_request.html")
    
    # Sprawdź też minimalny zestaw pól
    print("\n6. MINIMALNY ZESTAW PÓL:")
    minimal_fields = {
        'storename': '760995999',
        'chargetotal': '10.00',
        'currency': '985'
    }
    
    for k, v in minimal_fields.items():
        print(f"   {k}: {v}")
    
    import webbrowser
    import os
    webbrowser.open(f"file://{os.path.abspath('debug_exact_request.html')}")

if __name__ == "__main__":
    debug_exact_request()
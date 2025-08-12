#!/usr/bin/env python3
"""
Debug - dokładnie co wysyłamy dla combined page
"""

from datetime import datetime, timezone
from app.utils.fiserv_ipg_client import FiservIPGClient
import hmac
import hashlib
import base64
import json

def debug_combined_page():
    """Pokaż dokładnie co wysyłamy dla combined page"""
    
    print("="*60)
    print("DEBUG: COMBINED PAGE REQUEST")
    print("="*60)
    
    client = FiservIPGClient()
    
    # Przygotuj dane dokładnie jak w produkcji
    order_id = f"COMBINED-DEBUG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    amount = 10.00
    
    # Podstawowe pola dla combined page
    fields = {
        'storename': '760995999',
        'txntype': 'sale',
        'timezone': 'Europe/Berlin',
        'txndatetime': datetime.now(timezone.utc).strftime("%Y:%m:%d-%H:%M:%S"),
        'chargetotal': f"{amount:.2f}",
        'currency': '985',  # PLN
        'checkoutoption': 'combinedpage',  # TO JEST KLUCZOWE
        'oid': order_id,
        'hash_algorithm': 'HMACSHA256',
        # Dodaj adresy URL zgodnie z sugestią
        'responseSuccessURL': 'https://yourapp.ngrok.app/api/payments/success',
        'responseFailURL': 'https://yourapp.ngrok.app/api/payments/failure',
        'transactionNotificationURL': 'https://yourapp.ngrok.app/api/payments/webhooks/fiserv'
    }
    
    print("\n1. POLA FORMULARZA (przed hashem):")
    for k, v in sorted(fields.items()):
        print(f"   {k}: {v}")
    
    # Oblicz hash - dokładnie jak w kodzie
    hash_fields = {k: v for k, v in fields.items() if k not in ['hash_algorithm', 'hashExtended']}
    sorted_fields = sorted(hash_fields.items())
    hash_string = '|'.join(str(v) for k, v in sorted_fields)
    
    print(f"\n2. STRING DO HASHA (posortowane alfabetycznie):")
    print(f"   {hash_string}")
    
    print(f"\n3. OBLICZANIE HASHA:")
    print(f"   Secret: {client.shared_secret}")
    print(f"   Algorithm: HMAC-SHA256")
    
    # Oblicz hash
    hash_bytes = hmac.new(
        client.shared_secret.encode('utf-8'),
        hash_string.encode('utf-8'),
        hashlib.sha256
    ).digest()
    hash_value = base64.b64encode(hash_bytes).decode('utf-8')
    
    print(f"   Hash (Base64): {hash_value}")
    
    # Dodaj hash do pól
    fields['hashExtended'] = hash_value
    
    print(f"\n4. FINALNE POLA WYSYŁANE:")
    for k, v in sorted(fields.items()):
        if k == 'hashExtended':
            print(f"   {k}: {v[:40]}...")
        else:
            print(f"   {k}: {v}")
    
    print(f"\n5. ACTION URL:")
    print(f"   {client.gateway_url}")
    
    # Generuj test HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Debug Combined Page Request</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }}
        .debug {{ background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-radius: 5px; margin: 20px 0; }}
        .field {{ background: #e9ecef; padding: 10px; margin: 5px 0; font-family: monospace; }}
        button {{ background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        button:hover {{ background: #0056b3; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>🔍 Debug: Combined Page Request</h1>
    
    <div class="warning">
        <strong>⚠️ Problem:</strong> Combined Page daje validationError<br>
        <strong>Prawdopodobna przyczyna:</strong> Nieprawidłowy Shared Secret
    </div>
    
    <div class="debug">
        <h3>Co wysyłamy:</h3>
        <div class="field">URL: {client.gateway_url}</div>
        <div class="field">Method: POST</div>
        <div class="field">Content-Type: application/x-www-form-urlencoded</div>
    </div>
    
    <div class="debug">
        <h3>Pola formularza:</h3>
"""
    
    # Pokaż wszystkie pola
    for k, v in sorted(fields.items()):
        if k == 'hashExtended':
            html += f'        <div class="field">{k} = {v[:40]}...</div>\n'
        else:
            html += f'        <div class="field">{k} = {v}</div>\n'
    
    html += f"""    </div>
    
    <div class="debug">
        <h3>Hash calculation:</h3>
        <div class="field">Input string: {hash_string[:80]}...</div>
        <div class="field">Secret: {client.shared_secret}</div>
        <div class="field">Algorithm: HMAC-SHA256</div>
        <div class="field">Output: {hash_value}</div>
    </div>
    
    <form method="POST" action="{client.gateway_url}" target="_blank">
"""
    
    # Dodaj wszystkie pola jako hidden inputs
    for k, v in fields.items():
        html += f'        <input type="hidden" name="{k}" value="{v}">\n'
    
    html += """        <button type="submit">🚀 Wyślij Request do Fiserv</button>
    </form>
    
    <div class="warning">
        <h3>Co powinno się stać:</h3>
        <ol>
            <li>Formularz jest wysyłany do Fiserv</li>
            <li>Fiserv sprawdza hash</li>
            <li>Jeśli hash jest poprawny → pokazuje stronę płatności</li>
            <li>Jeśli hash jest niepoprawny → validationError</li>
        </ol>
        
        <p><strong>Otrzymujemy validationError = hash jest nieprawidłowy = Shared Secret jest zły</strong></p>
    </div>
    
    <div class="debug">
        <h3>🔐 Testowane Shared Secrets:</h3>
        <ul>
            <li>j}2W3P)Lwv ❌</li>
            <li>c7dP/$5PBx ❌</li>
            <li>aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG ❌</li>
        </ul>
        
        <p><strong>Wniosek:</strong> Żaden z testowanych secretów nie jest prawidłowy dla Combined Page.</p>
    </div>
</body>
</html>"""
    
    with open('debug_combined_page.html', 'w') as f:
        f.write(html)
    
    print("\n✅ Debug zapisany jako: debug_combined_page.html")
    
    # Pokaż też przykład curl
    print("\n6. PRZYKŁAD CURL:")
    curl_data = '&'.join([f"{k}={v}" for k, v in fields.items()])
    print(f"""
curl -X POST '{client.gateway_url}' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d '{curl_data}'
""")
    
    import webbrowser
    import os
    webbrowser.open(f"file://{os.path.abspath('debug_combined_page.html')}")

if __name__ == "__main__":
    debug_combined_page()
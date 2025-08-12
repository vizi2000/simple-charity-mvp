#!/usr/bin/env python3
"""
Sprawdź czy URLe są faktycznie wysyłane w formularzu
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.fiserv_ipg_client import FiservIPGClient

def check_urls():
    """Sprawdź dokładnie co jest wysyłane"""
    
    print("="*60)
    print("SPRAWDZENIE URLs W FORMULARZU")
    print("="*60)
    
    client = FiservIPGClient()
    
    # Generuj formularz
    form_data = client.create_payment_form_data(
        amount=50.00,
        order_id="URL-CHECK-TEST",
        description="Test URLs",
        success_url="https://charity.ngrok.app/platnosc/success",
        failure_url="https://charity.ngrok.app/platnosc/failure",
        notification_url="https://charity-webhook.ngrok.app/api/webhooks/fiserv",
        customer_info={
            "name": "Test User",
            "email": "test@example.com"
        }
    )
    
    fields = form_data['form_fields']
    
    print("\n📋 WSZYSTKIE POLA W FORMULARZU:")
    print("-" * 40)
    
    # Wypisz wszystkie pola
    for key in sorted(fields.keys()):
        value = fields[key]
        if 'URL' in key:
            print(f"🔗 {key:30} = {value}")
        elif key == 'hashExtended':
            print(f"   {key:30} = {value[:20]}... (len: {len(value)})")
        else:
            print(f"   {key:30} = {value}")
    
    print("\n🔍 ANALIZA URLs:")
    print("-" * 40)
    
    # Sprawdź które URLe są obecne
    url_fields = {
        'responseSuccessURL': 'URL sukcesu (wymagany)',
        'responseFailURL': 'URL niepowodzenia (wymagany)',
        'transactionNotificationURL': 'URL webhooks (opcjonalny)'
    }
    
    urls_present = []
    urls_missing = []
    
    for field, desc in url_fields.items():
        if field in fields and fields[field]:
            urls_present.append(field)
            print(f"✅ {field}:")
            print(f"   {desc}")
            print(f"   Wartość: {fields[field]}")
        else:
            urls_missing.append(field)
            print(f"❌ {field}:")
            print(f"   {desc}")
            print(f"   BRAK W FORMULARZU!")
    
    # Sprawdź czy URLe są w hash string
    print("\n🔐 CZY URLs SĄ W HASH STRING?")
    print("-" * 40)
    
    # Generuj hash string
    exclude_fields = {'hash', 'hashExtended', 'hash_algorithm'}
    hash_fields = {k: v for k, v in fields.items() if k not in exclude_fields}
    sorted_fields = sorted(hash_fields.items())
    hash_string = '|'.join(str(v) for k, v in sorted_fields)
    
    print("Hash string zawiera:")
    for url_field in url_fields.keys():
        if url_field in fields:
            url_value = fields[url_field]
            if url_value in hash_string:
                print(f"  ✅ {url_field}: TAK")
            else:
                print(f"  ❌ {url_field}: NIE (ale pole istnieje)")
        else:
            print(f"  ❌ {url_field}: NIE (pole nie istnieje)")
    
    # Pokaż cały hash string
    print(f"\nPełny hash string:")
    print(f"{hash_string}")
    
    # Generuj HTML do debugowania
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>URL Check Test</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Test URLs w formularzu</h1>
    <h2>Pola formularza:</h2>
    <form method="POST" action="{form_data['form_action']}">
"""
    
    for key, value in fields.items():
        html_content += f'        <div>{key}: <input type="text" name="{key}" value="{value}" readonly style="width: 600px;"></div>\n'
    
    html_content += """
        <button type="submit">Wyślij do Fiserv</button>
    </form>
</body>
</html>"""
    
    html_file = "check_urls_form.html"
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"\n📄 HTML z widocznymi polami: {html_file}")
    
    # Podsumowanie
    print("\n" + "="*60)
    print("PODSUMOWANIE:")
    print("="*60)
    
    if urls_missing:
        print(f"❌ PROBLEM: Brakuje {len(urls_missing)} URL(i):")
        for url in urls_missing:
            print(f"   - {url}")
    else:
        print("✅ Wszystkie URLe są obecne w formularzu")
        
    if urls_present:
        print(f"\n✅ Wysyłane URLe ({len(urls_present)}):")
        for url in urls_present:
            print(f"   - {url}: {fields[url][:50]}...")

if __name__ == "__main__":
    check_urls()
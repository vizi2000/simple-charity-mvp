#!/usr/bin/env python3
"""
Debug - sprawdź co dokładnie wysyłamy do Fiserv
"""

from datetime import datetime
from app.utils.fiserv_ipg_client import FiservIPGClient
import json

def debug_form_fields():
    """Sprawdź dokładnie jakie pola wysyłamy"""
    
    print("="*60)
    print("DEBUG: CO WYSYŁAMY DO FISERV")
    print("="*60)
    
    client = FiservIPGClient()
    
    # Generuj dane formularza
    form_data = client.create_payment_form_data(
        amount=10.00,
        order_id=f"DEBUG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        description="Debug test",
        success_url="https://example.com/success",
        failure_url="https://example.com/failure"
    )
    
    print("\n1. Action URL:")
    print(f"   {form_data['form_action']}")
    
    print("\n2. Pola formularza:")
    for key, value in sorted(form_data['form_fields'].items()):
        if key == 'hashExtended':
            print(f"   {key}: {value[:40]}...")
        else:
            print(f"   {key}: {value}")
    
    print("\n3. CZY WYSYŁAMY DANE KARTY?")
    card_fields = ['cardnumber', 'cardNumber', 'pan', 'ccnum', 'number', 'card']
    found_card_fields = []
    
    for field in form_data['form_fields']:
        if any(card_field in field.lower() for card_field in card_fields):
            found_card_fields.append(field)
    
    if found_card_fields:
        print("   ❌ TAK! Znaleziono pola karty:", found_card_fields)
        print("   TO JEST BŁĄD - nie powinniśmy wysyłać danych karty!")
    else:
        print("   ✅ NIE - poprawnie, dane karty wprowadza użytkownik na stronie Fiserv")
    
    print("\n4. Oczekiwany przepływ:")
    print("   1. Wysyłamy formularz z danymi transakcji (kwota, order_id, itp.)")
    print("   2. Fiserv pokazuje swoją stronę płatności")
    print("   3. Użytkownik wprowadza dane karty na stronie Fiserv")
    print("   4. Fiserv przetwarza płatność")
    print("   5. Przekierowanie na success/failure URL")
    
    # Generuj prosty HTML do testowania
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Debug Form</title>
    <style>
        body {{ font-family: monospace; max-width: 800px; margin: 50px auto; }}
        .field {{ background: #f0f0f0; padding: 5px; margin: 2px 0; }}
        button {{ background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
    </style>
</head>
<body>
    <h1>Debug: Formularz wysyłany do Fiserv</h1>
    
    <p><strong>Action URL:</strong> {form_data['form_action']}</p>
    
    <form method="POST" action="{form_data['form_action']}">
        <h3>Pola wysyłane (bez danych karty!):</h3>
"""
    
    for key, value in form_data['form_fields'].items():
        html += f'        <div class="field">{key}: <input type="text" name="{key}" value="{value}" readonly style="width: 500px;"></div>\n'
    
    html += """
        <p style="background: #d4edda; padding: 10px;">
            ✅ <strong>Poprawnie:</strong> Nie wysyłamy żadnych danych karty!<br>
            Dane karty użytkownik wprowadzi na stronie Fiserv.
        </p>
        
        <button type="submit">Wyślij do Fiserv (otworzy stronę płatności)</button>
    </form>
    
    <hr>
    
    <h3>Co powinno się stać:</h3>
    <ol>
        <li>Klikniesz przycisk</li>
        <li><strong>Fiserv wyświetli swoją stronę płatności</strong></li>
        <li>TAM wprowadzisz dane karty</li>
    </ol>
    
    <p style="background: #f8d7da; padding: 10px;">
        Jeśli dostajesz błąd ZANIM zobaczysz stronę do wprowadzenia karty,<br>
        to problem jest z konfiguracją konta lub parametrami transakcji.
    </p>
</body>
</html>"""
    
    with open('debug_form.html', 'w') as f:
        f.write(html)
    
    print("\n✅ Zapisano debug_form.html")
    print("\nSprawdź czy na stronie Fiserv możesz wprowadzić dane karty.")
    
    import webbrowser
    import os
    webbrowser.open(f"file://{os.path.abspath('debug_form.html')}")

if __name__ == "__main__":
    debug_form_fields()
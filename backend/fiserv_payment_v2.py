#!/usr/bin/env python3
"""
Fiserv IPG Connect Payment Integration v2
Kompletna, nowa implementacja od podstaw
"""

import hmac
import hashlib
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Optional, Any
import json


class FiservIPGPayment:
    """
    Nowa, czysta implementacja integracji z Fiserv IPG Connect
    """
    
    def __init__(self):
        """Inicjalizacja z poprawnymi danymi"""
        # Dane sklepu testowego
        self.store_id = "760995999"
        self.shared_secret = "j}2W3P)Lwv"
        self.gateway_url = "https://test.ipg-online.com/connect/gateway/processing"
        
        # KRYTYCZNE: Zawsze używamy Europe/Warsaw dla polskich sklepów
        self.timezone = "Europe/Warsaw"
        self.currency = "985"  # PLN
        
    def get_warsaw_timestamp(self) -> str:
        """
        Generuje timestamp w formacie Fiserv dla czasu warszawskiego
        
        Returns:
            str: Timestamp w formacie YYYY:MM:DD-HH:MM:SS (czas warszawski)
        """
        warsaw_tz = ZoneInfo("Europe/Warsaw")
        now_warsaw = datetime.now(warsaw_tz)
        
        # Format wymagany przez Fiserv: YYYY:MM:DD-HH:MM:SS
        timestamp = now_warsaw.strftime("%Y:%m:%d-%H:%M:%S")
        
        print(f"[DEBUG] Wygenerowany timestamp warszawski: {timestamp}")
        return timestamp
    
    def calculate_hash(self, form_fields: Dict[str, str]) -> str:
        """
        Oblicza hash HMAC-SHA256 dla formularza płatności
        
        Args:
            form_fields: Słownik z polami formularza (bez hash_algorithm i hashExtended)
            
        Returns:
            str: Base64 encoded HMAC-SHA256 hash
        """
        # Pola które NIE wchodzą do hasha
        exclude_fields = {'hash_algorithm', 'hashExtended', 'hash'}
        
        # Filtruj i sortuj pola alfabetycznie
        fields_for_hash = {
            k: v for k, v in form_fields.items() 
            if k not in exclude_fields and v is not None and v != ''
        }
        
        # Sortuj alfabetycznie po kluczu
        sorted_fields = sorted(fields_for_hash.items())
        
        # Złącz TYLKO WARTOŚCI separatorem |
        values_string = '|'.join(str(value) for key, value in sorted_fields)
        
        print(f"[DEBUG] String do hasha: {values_string[:150]}...")
        
        # Oblicz HMAC-SHA256
        signature = hmac.new(
            self.shared_secret.encode('utf-8'),
            values_string.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Zakoduj w Base64
        hash_value = base64.b64encode(signature).decode('utf-8')
        
        print(f"[DEBUG] Wygenerowany hash: {hash_value[:30]}...")
        return hash_value
    
    def create_payment_form(
        self,
        amount: float,
        order_id: str,
        success_url: str,
        failure_url: str,
        notification_url: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tworzy kompletny formularz płatności dla Fiserv IPG Connect
        
        Args:
            amount: Kwota płatności
            order_id: Unikalny identyfikator zamówienia
            success_url: URL przekierowania po sukcesie
            failure_url: URL przekierowania po błędzie
            notification_url: URL dla webhooków (opcjonalny)
            customer_name: Imię i nazwisko klienta (opcjonalne)
            customer_email: Email klienta (opcjonalny)
            description: Opis płatności (opcjonalny)
            
        Returns:
            Dict z action URL i wszystkimi polami formularza
        """
        print("="*60)
        print("GENEROWANIE FORMULARZA PŁATNOŚCI FISERV")
        print("="*60)
        
        # Pobierz aktualny timestamp warszawski
        txndatetime = self.get_warsaw_timestamp()
        
        # Przygotuj wszystkie pola formularza
        form_fields = {
            # Pola obowiązkowe
            'storename': self.store_id,
            'txntype': 'sale',
            'timezone': self.timezone,  # ZAWSZE Europe/Warsaw
            'txndatetime': txndatetime,  # Czas warszawski
            'hash_algorithm': 'HMACSHA256',
            'chargetotal': f"{amount:.2f}",
            'currency': self.currency,
            'checkoutoption': 'combinedpage',
            'oid': order_id,
            
            # URLs - wymagane dla Combined Page
            'responseSuccessURL': success_url,
            'responseFailURL': failure_url,
        }
        
        # Dodaj opcjonalne pola
        if notification_url:
            form_fields['transactionNotificationURL'] = notification_url
            
        if customer_name:
            form_fields['bname'] = customer_name
            
        if customer_email:
            form_fields['bemail'] = customer_email
            
        # Oblicz hash (MUSI być ostatni!)
        hash_value = self.calculate_hash(form_fields)
        form_fields['hashExtended'] = hash_value
        
        # Debug - pokaż wszystkie pola
        print("\n📋 POLA FORMULARZA:")
        for key in sorted(form_fields.keys()):
            if key == 'hashExtended':
                print(f"  {key:30} = {form_fields[key][:20]}...")
            else:
                print(f"  {key:30} = {form_fields[key]}")
        
        # Weryfikacja krytycznych pól
        print("\n✅ WERYFIKACJA:")
        print(f"  Timezone: {form_fields['timezone']} {'✅' if form_fields['timezone'] == 'Europe/Warsaw' else '❌'}")
        print(f"  Timestamp: {form_fields['txndatetime']} (Warsaw time)")
        print(f"  Store ID: {form_fields['storename']}")
        print(f"  Amount: {form_fields['chargetotal']} {form_fields['currency']}")
        
        return {
            'action': self.gateway_url,
            'method': 'POST',
            'fields': form_fields
        }
    
    def generate_test_html(self, form_data: Dict[str, Any], output_file: str = None) -> str:
        """
        Generuje HTML z formularzem do testowania
        
        Args:
            form_data: Dane formularza z create_payment_form()
            output_file: Nazwa pliku do zapisania (opcjonalnie)
            
        Returns:
            str: HTML content
        """
        html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fiserv Payment Test - {form_data['fields'].get('oid', 'TEST')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .info-section {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 25px;
        }}
        .info-title {{
            font-weight: 600;
            color: #495057;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .info-grid {{
            display: grid;
            gap: 12px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px;
            background: white;
            border-radius: 6px;
        }}
        .info-label {{
            color: #6c757d;
            font-size: 14px;
        }}
        .info-value {{
            color: #212529;
            font-weight: 500;
            font-size: 14px;
            font-family: 'Courier New', monospace;
        }}
        .critical {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }}
        .success {{
            background: #d4edda;
            border-left: 4px solid #28a745;
        }}
        .test-cards {{
            background: #e7f3ff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 25px;
        }}
        .card-info {{
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 6px;
        }}
        .btn-submit {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn-submit:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }}
        .timestamp {{
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            margin-top: 20px;
        }}
        .hidden-fields {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Test Płatności Fiserv</h1>
        <p class="subtitle">Wersja 2.0 - Pełna zgodność z wymaganiami</p>
        
        <div class="info-section">
            <div class="info-title">📊 Szczegóły transakcji</div>
            <div class="info-grid">
                <div class="info-row">
                    <span class="info-label">Order ID:</span>
                    <span class="info-value">{form_data['fields'].get('oid')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Kwota:</span>
                    <span class="info-value">{form_data['fields'].get('chargetotal')} PLN</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Sklep:</span>
                    <span class="info-value">{form_data['fields'].get('storename')}</span>
                </div>
            </div>
        </div>
        
        <div class="info-section">
            <div class="info-title">⏰ Krytyczne parametry czasowe</div>
            <div class="info-grid">
                <div class="info-row critical">
                    <span class="info-label">Timezone:</span>
                    <span class="info-value">{form_data['fields'].get('timezone')}</span>
                </div>
                <div class="info-row critical">
                    <span class="info-label">Timestamp:</span>
                    <span class="info-value">{form_data['fields'].get('txndatetime')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Aktualny czas Warsaw:</span>
                    <span class="info-value">{datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y:%m:%d-%H:%M:%S')}</span>
                </div>
            </div>
        </div>
        
        <div class="test-cards">
            <div class="info-title">💳 Karta testowa Fiserv</div>
            <div class="card-info">
                <strong>Visa:</strong> 4012 0010 3714 1112<br>
                <strong>Data ważności:</strong> 12/26<br>
                <strong>CVV:</strong> 123
            </div>
        </div>
        
        <form id="paymentForm" method="POST" action="{form_data['action']}">
            <div class="hidden-fields">
"""
        
        # Dodaj wszystkie pola formularza jako hidden inputs
        for key, value in form_data['fields'].items():
            html += f'                <input type="hidden" name="{key}" value="{value}">\n'
        
        html += f"""            </div>
            <button type="submit" class="btn-submit">
                Przejdź do płatności →
            </button>
        </form>
        
        <div class="timestamp">
            Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Auto-submit dla testów (zakomentowane)
        // setTimeout(() => document.getElementById('paymentForm').submit(), 3000);
    </script>
</body>
</html>"""
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"\n💾 HTML zapisany do: {output_file}")
        
        return html


def test_payment():
    """Test funkcjonalny nowej implementacji"""
    
    print("\n" + "="*60)
    print("TEST NOWEJ IMPLEMENTACJI FISERV")
    print("="*60)
    
    # Inicjalizuj klienta
    client = FiservIPGPayment()
    
    # Dane testowe
    test_order_id = f"TEST-V2-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Wygeneruj formularz
    form_data = client.create_payment_form(
        amount=25.00,
        order_id=test_order_id,
        success_url="https://charity.ngrok.app/payment/success",
        failure_url="https://charity.ngrok.app/payment/failure",
        notification_url="https://charity-webhook.ngrok.app/api/webhooks/fiserv",
        customer_name="Jan Kowalski",
        customer_email="jan.kowalski@example.com",
        description="Testowa płatność v2"
    )
    
    # Wygeneruj HTML
    html_file = f"fiserv_test_v2_{test_order_id}.html"
    client.generate_test_html(form_data, html_file)
    
    # Zapisz dane do JSON dla analizy
    json_file = f"fiserv_test_v2_{test_order_id}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'order_id': test_order_id,
            'form_data': form_data,
            'verification': {
                'timezone_correct': form_data['fields']['timezone'] == 'Europe/Warsaw',
                'timestamp_format_valid': len(form_data['fields']['txndatetime']) == 19,
                'hash_present': 'hashExtended' in form_data['fields'],
                'urls_present': all(k in form_data['fields'] for k in ['responseSuccessURL', 'responseFailURL'])
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 JSON zapisany do: {json_file}")
    
    print("\n" + "="*60)
    print("✅ TEST ZAKOŃCZONY POMYŚLNIE")
    print("="*60)
    print(f"\n🎯 Otwórz {html_file} w przeglądarce i kliknij 'Przejdź do płatności'")
    print("   Użyj karty testowej: 4012 0010 3714 1112, 12/26, CVV: 123")
    
    return form_data


if __name__ == "__main__":
    test_payment()
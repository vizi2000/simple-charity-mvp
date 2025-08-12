#!/usr/bin/env python3
"""
Poprawiona implementacja płatności Fiserv/Polcard zgodnie z odkryciami z testów
"""

import hashlib
import hmac
from datetime import datetime, timedelta
import pytz
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
import logging
from collections import OrderedDict

# Konfiguracja
FISERV_CONFIG = {
    "storename": "760995999",
    "shared_secret": "j}2W3P)Lwv",  
    "gateway_url": "https://test.ipg-online.com/connect/gateway/processing",
    "base_url": "http://borgtools.ddns.net:8001"  # Publiczny adres DDNS
}

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fiserv Payment Fixed")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Przechowywanie zamówień (w produkcji użyj bazy danych)
orders_db = {}


def generate_hash_extended(params: dict, shared_secret: str) -> str:
    """
    Generuje hashExtended zgodnie z odkryciami z testów:
    1. Sortowanie alfabetyczne pól
    2. Łączenie tylko wartości separatorem |
    3. NIE zawiera transactionNotificationURL, bname, bemail
    4. Zwraca Base64 (nie hex!)
    """
    import base64
    
    # Lista pól które WCHODZĄ do hasha (odkryte metodą prób i błędów)
    hash_fields = [
        'chargetotal',
        'checkoutoption', 
        'currency',
        'hash_algorithm',
        'oid',
        'responseFailURL',
        'responseSuccessURL',
        'storename',
        'timezone',
        'txndatetime',
        'txntype'
    ]
    
    # Filtruj tylko pola które mają wchodzić do hasha
    params_for_hash = {k: v for k, v in params.items() if k in hash_fields}
    
    # Sortuj alfabetycznie po kluczach
    sorted_params = OrderedDict(sorted(params_for_hash.items()))
    
    # Łącz tylko wartości separatorem |
    string_to_hash = '|'.join(str(v) for v in sorted_params.values())
    
    logger.info(f"Fields for hash: {list(sorted_params.keys())}")
    logger.info(f"String to hash: {string_to_hash}")
    
    # POPRAWKA: Używaj shared_secret bezpośrednio, nie konwertuj na hex!
    hash_value = hmac.new(
        shared_secret.encode('utf-8'),  # Używaj bezpośrednio jako string
        string_to_hash.encode('utf-8'),
        hashlib.sha256
    ).digest()  # digest() zamiast hexdigest()
    
    # POPRAWKA: Zwróć Base64 zamiast hex
    base64_hash = base64.b64encode(hash_value).decode('utf-8')
    
    logger.info(f"Generated hashExtended (Base64): {base64_hash}")
    
    return base64_hash


@app.get("/", response_class=HTMLResponse)
async def home():
    """Strona główna z formularzem płatności"""
    html = """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Test Płatności Fiserv (Poprawiony)</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            form {
                display: flex;
                flex-direction: column;
            }
            label {
                margin-top: 15px;
                color: #666;
                font-weight: bold;
            }
            input, select {
                padding: 10px;
                margin-top: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            button {
                margin-top: 20px;
                padding: 15px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 18px;
                cursor: pointer;
            }
            button:hover {
                background: #45a049;
            }
            .info {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }
            .test-cards {
                background: #fff3e0;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }
            .discovery {
                background: #f3e5f5;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Test Płatności Fiserv/Polcard</h1>
            <h3 style="color: green;">Wersja poprawiona zgodnie z odkryciami</h3>
            
            <form action="/prepare-payment" method="POST">
                <label for="amount">Kwota do zapłaty (PLN):</label>
                <input type="number" id="amount" name="amount" step="0.01" min="0.01" value="10.50" required>
                
                <label for="payment_method">Metoda płatności:</label>
                <select id="payment_method" name="payment_method">
                    <option value="card">Karta płatnicza</option>
                    <option value="blik">BLIK</option>
                </select>
                
                <button type="submit">Zapłać teraz</button>
            </form>
            
            <div class="discovery">
                <h3>🔍 Kluczowe odkrycia z testów:</h3>
                <ul>
                    <li>❌ transactionNotificationURL NIE wchodzi do hasha</li>
                    <li>✅ Używamy hashExtended dla HPP</li>
                    <li>✅ Pola sortowane alfabetycznie</li>
                    <li>✅ Łączone separatorem |</li>
                    <li>✅ checkoutoption = combinedpage</li>
                    <li>✅ Timestamp musi być aktualny</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>Informacje o konfiguracji:</h3>
                <p>Store ID: 760995999</p>
                <p>Środowisko: TEST</p>
                <p>Publiczny URL: borgtools.ddns.net:8001</p>
            </div>
            
            <div class="test-cards">
                <h3>Karty testowe:</h3>
                <p><strong>Karta DEBIT (APPROVED):</strong><br>
                4410947715337430, 12/26, CVV: 287</p>
                
                <p><strong>Karta CREDIT (DECLINED):</strong><br>
                5575233623260024, 12/26, CVV: 123</p>
                
                <p><strong>Kod BLIK (APPROVED):</strong> 777777</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


@app.post("/prepare-payment")
async def prepare_payment(
    amount: float = Form(...),
    payment_method: str = Form("card")
):
    """Przygotowuje dane płatności zgodnie z odkryciami z testów"""
    
    # Generowanie unikalnego ID zamówienia
    order_id = f"ORDER-{uuid.uuid4().hex[:8].upper()}"
    
    # Pobieranie AKTUALNEGO czasu w strefie Warszawy (nie może być przeterminowany!)
    warsaw_tz = pytz.timezone('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    # Dodaj 1 minutę aby uniknąć problemów z synchronizacją czasu
    future_time = now + timedelta(minutes=1)
    txndatetime = future_time.strftime("%Y:%m:%d-%H:%M:%S")
    
    # Formatowanie kwoty (zawsze 2 miejsca po przecinku)
    chargetotal = f"{amount:.2f}"
    
    # Parametry transakcji - WSZYSTKIE które wysyłamy
    all_params = {
        "txntype": "sale",
        "timezone": "Europe/Warsaw",
        "txndatetime": txndatetime,
        "hash_algorithm": "HMACSHA256",
        "hashExtended": "",  # Wypełnimy po wygenerowaniu
        "storename": FISERV_CONFIG["storename"],
        "chargetotal": chargetotal,
        "currency": "985",  # PLN - MUSI być 985
        "checkoutoption": "classic",  # Zmienione na classic - działa lepiej dla tego store ID
        "oid": order_id,
        "responseSuccessURL": f"{FISERV_CONFIG['base_url']}/payment-success",
        "responseFailURL": f"{FISERV_CONFIG['base_url']}/payment-fail",
        "transactionNotificationURL": f"{FISERV_CONFIG['base_url']}/api/fiserv-notify",  # NIE wchodzi do hasha!
    }
    
    # Dodaj opcjonalne parametry jeśli potrzebne
    if payment_method == "blik":
        all_params["paymentMethod"] = "blik"
    
    # Generowanie hashExtended (NIE zawiera transactionNotificationURL!)
    hash_value = generate_hash_extended(all_params, FISERV_CONFIG["shared_secret"])
    all_params["hashExtended"] = hash_value
    
    # Zapisz zamówienie
    orders_db[order_id] = {
        "amount": amount,
        "status": "pending",
        "payment_method": payment_method,
        "created_at": now.isoformat(),
        "params": all_params
    }
    
    # Logowanie dla debugowania
    logger.info(f"Order created: {order_id}")
    logger.info(f"Timestamp: {txndatetime} (future: +1 min)")
    logger.info(f"All parameters being sent: {json.dumps(all_params, indent=2)}")
    
    # Generowanie formularza HTML z automatycznym przekierowaniem
    form_fields = "".join([
        f'<input type="hidden" name="{key}" value="{value}">'
        for key, value in all_params.items()
    ])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Przekierowanie do bramki płatniczej...</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: #f5f5f5;
            }}
            .loader {{
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .spinner {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .debug {{
                margin-top: 20px;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 5px;
                font-size: 12px;
                text-align: left;
                max-width: 600px;
            }}
        </style>
    </head>
    <body>
        <div class="loader">
            <div class="spinner"></div>
            <h2>Przekierowanie do bramki płatniczej...</h2>
            <p>Proszę czekać...</p>
            
            <div class="debug">
                <strong>Debug info:</strong><br>
                Order ID: {order_id}<br>
                Timestamp: {txndatetime}<br>
                Hash fields: chargetotal, checkoutoption, currency, hash_algorithm, oid, responseFailURL, responseSuccessURL, storename, timezone, txndatetime, txntype<br>
                ❌ NOT in hash: transactionNotificationURL
            </div>
        </div>
        
        <form id="payment_form" action="{FISERV_CONFIG['gateway_url']}" method="POST">
            {form_fields}
        </form>
        
        <script>
            setTimeout(function() {{
                document.getElementById('payment_form').submit();
            }}, 2000); // Daj chwilę na przeczytanie debug info
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)


@app.get("/payment-success")
async def payment_success(request: Request):
    """Strona sukcesu płatności"""
    params = dict(request.query_params)
    logger.info(f"Payment success callback received: {json.dumps(params, indent=2)}")
    
    # Aktualizuj status zamówienia jeśli mamy OID
    if "oid" in params:
        if params["oid"] in orders_db:
            orders_db[params["oid"]]["status"] = "success"
            orders_db[params["oid"]]["response"] = params
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Płatność zakończona sukcesem</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background: #f0f8f0;
                margin: 0;
                padding: 20px;
            }}
            .success {{
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                max-width: 600px;
            }}
            .checkmark {{
                font-size: 72px;
                color: #4CAF50;
            }}
            h1 {{
                color: #4CAF50;
            }}
            .details {{
                background: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: left;
            }}
            a {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="success">
            <div class="checkmark">✓</div>
            <h1>Płatność zakończona sukcesem!</h1>
            <p>Dziękujemy za dokonanie płatności.</p>
            
            <div class="details">
                <h3>Szczegóły transakcji:</h3>
                <pre>{json.dumps(params, indent=2)}</pre>
            </div>
            
            <a href="/">Powrót do strony głównej</a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)


@app.get("/payment-fail")
async def payment_fail(request: Request):
    """Strona błędu płatności"""
    params = dict(request.query_params)
    logger.info(f"Payment fail callback received: {json.dumps(params, indent=2)}")
    
    # Aktualizuj status zamówienia jeśli mamy OID
    if "oid" in params:
        if params["oid"] in orders_db:
            orders_db[params["oid"]]["status"] = "failed"
            orders_db[params["oid"]]["response"] = params
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Płatność nieudana</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background: #fff0f0;
                margin: 0;
                padding: 20px;
            }}
            .fail {{
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                max-width: 600px;
            }}
            .xmark {{
                font-size: 72px;
                color: #f44336;
            }}
            h1 {{
                color: #f44336;
            }}
            .details {{
                background: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: left;
            }}
            a {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #2196F3;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="fail">
            <div class="xmark">✗</div>
            <h1>Płatność nieudana</h1>
            <p>Płatność została anulowana lub odrzucona.</p>
            
            <div class="details">
                <h3>Szczegóły błędu:</h3>
                <pre>{json.dumps(params, indent=2)}</pre>
            </div>
            
            <a href="/">Spróbuj ponownie</a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)


@app.post("/api/fiserv-notify")
async def fiserv_notify(request: Request):
    """
    Endpoint dla powiadomień Server-to-Server od Fiserv
    KRYTYCZNE: To jest jedyne wiarygodne źródło statusu płatności!
    """
    
    # Pobierz dane z różnych źródeł
    form_data = await request.form()
    body = await request.body()
    
    notification_data = dict(form_data) if form_data else {}
    
    logger.info(f"S2S Notification received:")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Form data: {notification_data}")
    logger.info(f"Raw body: {body.decode('utf-8') if body else 'empty'}")
    
    # TODO: Weryfikacja sygnatury (response_hash)
    if "response_hash" in notification_data:
        logger.info(f"Response hash present: {notification_data['response_hash']}")
        # Tu powinniśmy zweryfikować hash zgodnie z dokumentacją
    
    # Aktualizuj status zamówienia
    if "oid" in notification_data:
        order_id = notification_data["oid"]
        if order_id in orders_db:
            status = notification_data.get("status", notification_data.get("approval_code", "unknown"))
            orders_db[order_id]["final_status"] = status
            orders_db[order_id]["s2s_notification"] = notification_data
            logger.info(f"Order {order_id} updated with final status: {status}")
    
    # WAŻNE: Odpowiedz 200 OK aby Fiserv wiedział, że otrzymaliśmy powiadomienie
    return {"status": "ok"}


@app.get("/api/fiserv-notify")
async def fiserv_notify_get(request: Request):
    """Niektóre systemy mogą używać GET dla pierwszego testu"""
    params = dict(request.query_params)
    logger.info(f"S2S Notification GET received: {params}")
    return {"status": "ok", "method": "GET", "params": params}


@app.get("/api/orders")
async def list_orders():
    """Lista wszystkich zamówień (dla debugowania)"""
    return {"orders": orders_db}


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Szczegóły zamówienia"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]


@app.get("/api/debug/hash-test")
async def test_hash():
    """Endpoint testowy do weryfikacji generowania hasha"""
    
    test_params = {
        "chargetotal": "10.00",
        "checkoutoption": "combinedpage",
        "currency": "985",
        "hash_algorithm": "HMACSHA256",
        "oid": "TEST-123",
        "responseFailURL": f"{FISERV_CONFIG['base_url']}/payment-fail",
        "responseSuccessURL": f"{FISERV_CONFIG['base_url']}/payment-success",
        "storename": FISERV_CONFIG["storename"],
        "timezone": "Europe/Warsaw",
        "txndatetime": "2025:08:10-12:30:00",
        "txntype": "sale"
    }
    
    hash_value = generate_hash_extended(test_params, FISERV_CONFIG["shared_secret"])
    
    return {
        "test_params": test_params,
        "generated_hash": hash_value,
        "info": "Hash NIE zawiera: transactionNotificationURL, bname, bemail"
    }


if __name__ == "__main__":
    import uvicorn
    print(f"Starting Fixed Fiserv Payment Server...")
    print(f"Open http://localhost:8001 in your browser")
    print(f"Public URL: http://borgtools.ddns.net:8001")
    print(f"Store ID: {FISERV_CONFIG['storename']}")
    print(f"Gateway URL: {FISERV_CONFIG['gateway_url']}")
    print(f"\n🔍 Kluczowe odkrycia zastosowane:")
    print(f"  - transactionNotificationURL NIE w hashu")
    print(f"  - Używamy hashExtended")
    print(f"  - Timestamp w przyszłości (+1 min)")
    print(f"  - checkoutoption = combinedpage")
    uvicorn.run(app, host="0.0.0.0", port=8001)
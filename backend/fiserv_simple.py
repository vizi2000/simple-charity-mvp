#!/usr/bin/env python3
"""
Prosta implementacja płatności Fiserv/Polcard zgodnie z przewodnikiem
"""

import hashlib
import hmac
from datetime import datetime
import pytz
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
import logging

# Konfiguracja
FISERV_CONFIG = {
    "storename": "760995999",
    "shared_secret": "j}2W3P)Lwv",  # Klucz z przewodnika
    "api_key": "xWdewnCcYTy8G0s4oS1r5GAOmcdVRYQn",
    "secret_key": "aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG",
    "gateway_url": "https://test.ipg-online.com/connect/gateway/processing",
    "base_url": "http://borgtools.ddns.net:8001"  # Publiczny adres DDNS
}

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fiserv Payment Simple")

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


def generate_hash(storename: str, txndatetime: str, chargetotal: str, currency: str, shared_secret: str) -> str:
    """
    Generuje hash HMAC-SHA256 zgodnie z dokumentacją Fiserv
    """
    # Tworzenie ciągu do hashowania
    string_to_hash = f"{storename}{txndatetime}{chargetotal}{currency}{shared_secret}"
    
    logger.info(f"String to hash: {string_to_hash}")
    
    # Konwertowanie shared_secret na hex
    secret_hex = shared_secret.encode('utf-8').hex()
    
    # Obliczanie HMAC-SHA256
    hash_value = hmac.new(
        bytes.fromhex(secret_hex),
        string_to_hash.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    logger.info(f"Generated hash: {hash_value}")
    
    return hash_value


@app.get("/", response_class=HTMLResponse)
async def home():
    """Strona główna z formularzem płatności"""
    html = """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Test Płatności Fiserv</title>
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
            input {
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Test Płatności Fiserv/Polcard</h1>
            
            <form action="/prepare-payment" method="POST">
                <label for="amount">Kwota do zapłaty (PLN):</label>
                <input type="number" id="amount" name="amount" step="0.01" min="0.01" value="10.50" required>
                
                <button type="submit">Zapłać teraz</button>
            </form>
            
            <div class="info">
                <h3>Informacje o testach:</h3>
                <p>To jest środowisko testowe Fiserv.</p>
                <p>Store ID: 760995999</p>
            </div>
            
            <div class="test-cards">
                <h3>Karty testowe:</h3>
                <p><strong>Karta DEBIT (APPROVED):</strong><br>
                Numer: 4410947715337430<br>
                Data: 12/26<br>
                CVV: 287</p>
                
                <p><strong>Karta CREDIT (DECLINED):</strong><br>
                Numer: 5575233623260024<br>
                Data: 12/26<br>
                CVV: 123</p>
                
                <p><strong>Kod BLIK (APPROVED):</strong> 777777</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


@app.post("/prepare-payment")
async def prepare_payment(amount: float = Form(...)):
    """Przygotowuje dane płatności i przekierowuje do Fiserv"""
    
    # Generowanie unikalnego ID zamówienia
    order_id = f"ORDER-{uuid.uuid4().hex[:8].upper()}"
    
    # Pobieranie aktualnego czasu w strefie Warszawy
    warsaw_tz = pytz.timezone('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    txndatetime = now.strftime("%Y:%m:%d-%H:%M:%S")
    
    # Formatowanie kwoty (zawsze 2 miejsca po przecinku)
    chargetotal = f"{amount:.2f}"
    
    # Parametry transakcji
    params = {
        "txntype": "sale",
        "timezone": "Europe/Warsaw",
        "txndatetime": txndatetime,
        "hash_algorithm": "HMACSHA256",
        "storename": FISERV_CONFIG["storename"],
        "chargetotal": chargetotal,
        "currency": "985",  # PLN
        "oid": order_id,
        "responseSuccessURL": f"{FISERV_CONFIG['base_url']}/payment-success",
        "responseFailURL": f"{FISERV_CONFIG['base_url']}/payment-fail",
        "transactionNotificationURL": f"{FISERV_CONFIG['base_url']}/api/fiserv-notify"
    }
    
    # Generowanie hash
    hash_value = generate_hash(
        params["storename"],
        params["txndatetime"],
        params["chargetotal"],
        params["currency"],
        FISERV_CONFIG["shared_secret"]
    )
    params["hash"] = hash_value
    
    # Zapisz zamówienie
    orders_db[order_id] = {
        "amount": amount,
        "status": "pending",
        "created_at": now.isoformat(),
        "params": params
    }
    
    # Logowanie dla debugowania
    logger.info(f"Order created: {order_id}")
    logger.info(f"Parameters: {json.dumps(params, indent=2)}")
    
    # Generowanie formularza HTML z automatycznym przekierowaniem
    form_fields = "".join([
        f'<input type="hidden" name="{key}" value="{value}">'
        for key, value in params.items()
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
        </style>
    </head>
    <body>
        <div class="loader">
            <div class="spinner"></div>
            <h2>Przekierowanie do bramki płatniczej...</h2>
            <p>Proszę czekać...</p>
        </div>
        
        <form id="payment_form" action="{FISERV_CONFIG['gateway_url']}" method="POST">
            {form_fields}
        </form>
        
        <script>
            document.getElementById('payment_form').submit();
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
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Płatność zakończona sukcesem</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: #f0f8f0;
            }
            .success {
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .checkmark {
                font-size: 72px;
                color: #4CAF50;
            }
            h1 {
                color: #4CAF50;
            }
            a {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="success">
            <div class="checkmark">✓</div>
            <h1>Płatność zakończona sukcesem!</h1>
            <p>Dziękujemy za dokonanie płatności.</p>
            <a href="/">Powrót do strony głównej</a>
        </div>
    </body>
    </html>
    """
    
    # Aktualizuj status zamówienia jeśli mamy OID
    if "oid" in params:
        if params["oid"] in orders_db:
            orders_db[params["oid"]]["status"] = "success"
            orders_db[params["oid"]]["response"] = params
    
    return HTMLResponse(content=html)


@app.get("/payment-fail")
async def payment_fail(request: Request):
    """Strona błędu płatności"""
    params = dict(request.query_params)
    logger.info(f"Payment fail callback received: {json.dumps(params, indent=2)}")
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Płatność nieudana</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: #fff0f0;
            }
            .fail {
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .xmark {
                font-size: 72px;
                color: #f44336;
            }
            h1 {
                color: #f44336;
            }
            a {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #2196F3;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="fail">
            <div class="xmark">✗</div>
            <h1>Płatność nieudana</h1>
            <p>Płatność została anulowana lub odrzucona.</p>
            <a href="/">Spróbuj ponownie</a>
        </div>
    </body>
    </html>
    """
    
    # Aktualizuj status zamówienia jeśli mamy OID
    if "oid" in params:
        if params["oid"] in orders_db:
            orders_db[params["oid"]]["status"] = "failed"
            orders_db[params["oid"]]["response"] = params
    
    return HTMLResponse(content=html)


@app.post("/api/fiserv-notify")
async def fiserv_notify(request: Request):
    """Endpoint dla powiadomień Server-to-Server od Fiserv"""
    
    # Pobierz dane z różnych źródeł
    form_data = await request.form()
    body = await request.body()
    
    notification_data = dict(form_data) if form_data else {}
    
    logger.info(f"S2S Notification received:")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Form data: {notification_data}")
    logger.info(f"Raw body: {body.decode('utf-8') if body else 'empty'}")
    
    # Weryfikacja sygnatury (hash)
    if "response_hash" in notification_data:
        # TODO: Zweryfikuj hash zgodnie z dokumentacją Fiserv
        logger.info(f"Response hash: {notification_data['response_hash']}")
    
    # Aktualizuj status zamówienia
    if "oid" in notification_data:
        order_id = notification_data["oid"]
        if order_id in orders_db:
            status = notification_data.get("status", "unknown")
            orders_db[order_id]["status"] = status
            orders_db[order_id]["s2s_notification"] = notification_data
            logger.info(f"Order {order_id} updated with status: {status}")
    
    # Odpowiedz 200 OK aby Fiserv wiedział, że otrzymaliśmy powiadomienie
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


if __name__ == "__main__":
    import uvicorn
    print(f"Starting Fiserv Payment Server...")
    print(f"Open http://localhost:8001 in your browser")
    print(f"Store ID: {FISERV_CONFIG['storename']}")
    print(f"Gateway URL: {FISERV_CONFIG['gateway_url']}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
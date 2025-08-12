# Przewodnik Sprawdzania Aktywności Konta Fiserv

## 1. Virtual Terminal - Krok po Kroku

### Logowanie
1. Otwórz: https://test.ipg-online.com/vt/
2. Zaloguj się:
   - **Store Name/Login:** 760995999
   - **Password:** c7dP/$5PBx

### Co sprawdzić po zalogowaniu:

#### A. Dashboard/Status
- Czy widzisz dashboard bez błędów?
- Czy są jakieś ostrzeżenia o nieaktywnym koncie?
- Czy wyświetla się status "Active" lub "Test Mode"?

#### B. Ręczna transakcja testowa
1. Kliknij "New Transaction" lub "Sale"
2. Wypełnij:
   - Amount: 10.00
   - Currency: EUR (lub sprawdź dostępne waluty)
   - Card Number: 4005550000000019
   - Exp Date: 12/25
   - CVV: 111
3. Spróbuj przetworzyć transakcję
4. Jeśli otrzymasz sukces = konto aktywne
5. Jeśli błąd = zapisz dokładny komunikat

#### C. Sprawdź konfigurację
1. Szukaj sekcji "Settings" lub "Configuration"
2. Sprawdź:
   - Enabled Payment Methods
   - Supported Currencies
   - API Settings
   - Hash Algorithm (powinno być HMACSHA256)

#### D. Raporty
1. Przejdź do "Reports" lub "Transaction History"
2. Sprawdź czy widzisz wcześniejsze próby transakcji
3. Poszukaj swoich Order ID (np. 6067bc19-0478-46b3-a151-2b16f3162269)

## 2. Test API Status

Utwórz prosty test sprawdzający status:

```python
#!/usr/bin/env python3
import requests
import base64

# Test podstawowego połączenia z API
def test_api_connection():
    api_key = "xWdewnCcYTy8G0s4oS1r5GAOmcdVRYQn"
    api_secret = "aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG"
    
    # Podstawowa autoryzacja
    credentials = f"{api_key}:{api_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }
    
    # Próba połączenia z API
    test_endpoints = [
        "https://test.ipg-online.com/api/v1/stores/760995999",
        "https://test.ipg-online.com/api/v1/payment-methods",
        "https://test.ipg-online.com/api/v1/currencies"
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"\n{endpoint}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("Response:", response.json())
            else:
                print("Error:", response.text)
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    test_api_connection()
```

## 3. Minimalna Transakcja Testowa

Spróbuj najbardziej podstawowej transakcji:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fiserv Account Test</title>
</head>
<body>
    <h1>Test Konta Fiserv</h1>
    <form method="POST" action="https://test.ipg-online.com/connect/gateway/processing">
        <!-- Absolutne minimum pól -->
        <input type="hidden" name="txntype" value="sale">
        <input type="hidden" name="timezone" value="Europe/Berlin">
        <input type="hidden" name="txndatetime" value="2025:07:28-21:00:00">
        <input type="hidden" name="hash_algorithm" value="HMACSHA256">
        <input type="hidden" name="storename" value="760995999">
        <input type="hidden" name="chargetotal" value="1.00">
        <input type="hidden" name="currency" value="978">
        <input type="hidden" name="checkoutoption" value="combinedpage">
        
        <button type="submit">Test Account</button>
    </form>
</body>
</html>
```

## 4. Komunikaty Błędów - Co Oznaczają

### Konto Nieaktywne:
- "Store not found"
- "Invalid store ID"
- "Store is not active"
- "Merchant account disabled"

### Problem z Konfiguracją:
- "Currency not supported"
- "Payment method not enabled"
- "Invalid credentials"

### Błąd Aplikacji (obecny problem):
- "Unknown application error"
- "Transakcja nie może być zakończona"
- Może oznaczać: niepełną konfigurację, brak przypisanych uprawnień

## 5. Kontakt z Supportem

Jeśli Virtual Terminal nie działa lub pokazuje błędy:

### Przygotuj informacje:
```
Store ID: 760995999
Environment: Test/Sandbox
API Key: xWdewnCcYTy8G0s4oS1r5GAOmcdVRYQn
Issue: Cannot process test transactions - "Unknown application error"
Virtual Terminal Access: [czy możesz się zalogować?]
Test performed: [data i godzina]
```

### Pytania do supportu:
1. Is the test store 760995999 fully activated?
2. Which currencies are enabled for this store?
3. Are card payments enabled?
4. Is BLIK payment method enabled?
5. Is the hash algorithm set to HMACSHA256?
6. Are there any IP restrictions?

## 6. Alternatywne Testy

### A. Sprawdź różne przeglądarki
Czasem problemy z cookies/sesją

### B. Sprawdź różne karty testowe
```
Visa: 4005550000000019
Mastercard: 5204740000001002
Visa (alt): 4176660000000100
```

### C. Sprawdź różne kwoty
- 1.00 EUR (minimalna)
- 10.00 EUR
- 100.00 EUR

## Podsumowanie

1. **Najpierw** - Zaloguj się do Virtual Terminal
2. **Jeśli działa** - Spróbuj ręcznej transakcji
3. **Jeśli nie działa** - Konto prawdopodobnie nieaktywne
4. **Kontakt z supportem** - Z konkretnymi pytaniami
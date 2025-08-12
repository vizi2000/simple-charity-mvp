# Implementacja Płatności Fiserv/Polcard (HPP)

## 🚀 Szybki Start

### 1. Instalacja zależności

```bash
cd backend
source venv2/bin/activate  # lub stwórz nowy: python3 -m venv venv2
pip install fastapi uvicorn pytz
```

### 2. Uruchomienie serwera testowego

```bash
python fiserv_simple.py
```

Serwer uruchomi się na http://localhost:8001

### 3. Testowanie płatności

Otwórz http://localhost:8001 w przeglądarce i przetestuj płatność.

## 📝 Dane Testowe

### Konfiguracja
- **Store ID:** 760995999
- **Shared Secret:** j}2W3P)Lwv
- **Środowisko:** TEST (https://test.ipg-online.com)

### Karty Testowe

#### ✅ Scenariusz A: Płatność ZATWIERDZONA (Karta DEBIT)
- **Numer karty:** 4410947715337430
- **Data ważności:** 12/26
- **CVV:** 287
- **Rezultat:** APPROVED

#### ❌ Scenariusz C: Płatność ODRZUCONA (Karta CREDIT)
- **Numer karty:** 5575233623260024
- **Data ważności:** 12/26
- **CVV:** 123
- **Rezultat:** DECLINED

#### ✅ Scenariusz B: Płatność BLIK
- **Kod BLIK:** 777777
- **Rezultat:** APPROVED

## 🔧 Struktura Plików

```
backend/
├── fiserv_simple.py         # Główny serwer z implementacją
├── test_fiserv_guide.py     # Skrypt testowy do weryfikacji hash
└── README_FISERV.md         # Ten plik
```

## 📋 Endpointy API

### Frontend
- `GET /` - Strona główna z formularzem
- `POST /prepare-payment` - Przygotowanie i przekierowanie do Fiserv
- `GET /payment-success` - Strona sukcesu (responseSuccessURL)
- `GET /payment-fail` - Strona błędu (responseFailURL)

### Backend API
- `POST /api/fiserv-notify` - Webhook S2S od Fiserv (transactionNotificationURL)
- `GET /api/orders` - Lista wszystkich zamówień (debug)
- `GET /api/orders/{order_id}` - Szczegóły zamówienia

## 🔐 Proces Płatności

1. **Użytkownik** wypełnia formularz z kwotą
2. **Backend** przygotowuje parametry transakcji:
   - Generuje unikalny Order ID
   - Oblicza hash HMAC-SHA256
   - Tworzy formularz HTML
3. **Przekierowanie** do bramki Fiserv
4. **Użytkownik** dokonuje płatności na stronie Fiserv
5. **Powrót** na responseSuccessURL lub responseFailURL
6. **Webhook S2S** potwierdza status transakcji (KRYTYCZNE!)

## 🔍 Debugowanie

### Sprawdzenie logów
```bash
# Logi serwera pojawiają się w konsoli
# Każde żądanie i odpowiedź jest logowane
```

### Testowanie hash
```bash
python test_fiserv_guide.py
```

### Lista zamówień
```bash
curl http://localhost:8001/api/orders
```

## ⚠️ Ważne Uwagi

1. **URLs muszą być dostępne z internetu** dla webhooków S2S
   - Użyj ngrok dla testów lokalnych: `ngrok http 8001`
   - Zaktualizuj `base_url` w `fiserv_simple.py`

2. **Weryfikacja hash w webhookach** jest KRYTYCZNA dla bezpieczeństwa
   - Zawsze weryfikuj response_hash od Fiserv
   - Nigdy nie ufaj parametrom bez weryfikacji

3. **Status płatności** 
   - Jedynym wiarygodnym źródłem jest webhook S2S
   - ResponseSuccessURL to tylko informacja dla użytkownika

## 📱 Integracja z Istniejącą Aplikacją

Aby zintegrować z istniejącą aplikacją React:

1. Zamień endpoint formularza na `/api/payments/prepare`
2. Użyj axios do wysłania kwoty:
   ```javascript
   const response = await axios.post('/api/payments/prepare', {
     amount: 10.50
   });
   // response.data zawiera HTML formularza
   ```
3. Renderuj formularz i auto-submit
4. Obsłuż powroty w React Router

## 🐛 Rozwiązywanie Problemów

### "Unknown application error"
- Sprawdź poprawność Shared Secret
- Zweryfikuj format daty/czasu (YYYY:MM:DD-HH:mm:ss)
- Upewnij się, że kwota ma 2 miejsca po przecinku

### Brak webhooków S2S
- Sprawdź czy URL jest dostępny z internetu
- Zweryfikuj logi serwera
- Testuj z ngrok

### Hash nie pasuje
- Sprawdź kolejność pól w ciągu do hashowania
- Zweryfikuj encoding (UTF-8)
- Użyj `test_fiserv_guide.py` do debugowania

## 📞 Wsparcie

W razie problemów z integracją:
1. Sprawdź logi serwera
2. Użyj `test_fiserv_guide.py` do weryfikacji
3. Kontakt z Fiserv Support: podaj Store ID 760995999
# Raport Końcowych Zmian - Integracja Fiserv IPG

**Data:** 28 lipca 2025  
**Status:** Wszystkie zalecane zmiany wprowadzone

## Wprowadzone Modyfikacje

### 1. ✅ Zmiana pola `hash` na `hashExtended`

**Lokalizacja:** `/backend/app/utils/fiserv_ipg_client.py:73`

```python
form_fields['hashExtended'] = hash_value  # Use hashExtended as per IPG Connect docs
```

**Uzasadnienie:** Dokumentacja IPG Connect używa `hashExtended` w przykładowych formularzach.

### 2. ✅ Zmiana strefy czasowej

**Lokalizacja:** `/backend/app/utils/fiserv_ipg_client.py:39`

```python
'timezone': 'Europe/Berlin',  # Use supported timezone from docs
```

**Uzasadnienie:** `Europe/Warsaw` nie występuje w przykładach Fiserv. `Europe/Berlin` jest potwierdzoną strefą w dokumentacji.

### 3. ✅ Zmiana waluty na EUR (978)

**Lokalizacja:** `/backend/app/utils/fiserv_ipg_client.py:43`

```python
'currency': '978',  # EUR for testing (was PLN 985)
```

**Uzasadnienie:** Konto testowe może nie mieć włączonej obsługi PLN. EUR jest uniwersalnie wspierane.

### 4. ✅ Usunięcie polskich znaków diakrytycznych

**Lokalizacja:** `/backend/app/utils/fiserv_ipg_client.py:82-92`

Dodano metodę `_sanitize_text()` która zamienia:
- ą→a, ć→c, ę→e, ł→l, ń→n, ó→o, ś→s, ź→z, ż→z

**Przykład:** "Ofiara na kościół" → "Ofiara na kosciol"

### 5. ✅ Dodanie explicite parametru `paymentMethod`

**Lokalizacja:** `/backend/app/utils/fiserv_ipg_client.py:65-69`

```python
if payment_method == 'blik':
    form_fields['blikPayment'] = 'true'
    form_fields['paymentMethod'] = 'blik'
elif payment_method == 'card':
    form_fields['paymentMethod'] = 'card'  # Explicitly set payment method
```

**Uzasadnienie:** Jawne wskazanie metody płatności może pomóc gateway w interpretacji żądania.

## Przykład Wygenerowanego Formularza (Po Zmianach)

```json
{
  "storename": "760995999",
  "txntype": "sale",
  "timezone": "Europe/Berlin",
  "txndatetime": "2025:07:28-20:25:28",
  "hash_algorithm": "HMACSHA256",
  "chargetotal": "50.00",
  "currency": "978",
  "checkoutoption": "combinedpage",
  "oid": "6067bc19-0478-46b3-a151-2b16f3162269",
  "comments": "Darowizna na cel: Ofiara na kosciol",
  "responseSuccessURL": "http://localhost:5174/platnosc/...",
  "responseFailURL": "http://localhost:5174/platnosc/...",
  "language": "pl_PL",
  "authenticateTransaction": "true",
  "transactionNotificationURL": "https://77597ddbcc37.ngrok-free.app/api/webhooks/fiserv",
  "bname": "Test User",
  "bemail": "test@example.com",
  "paymentMethod": "card",
  "hashExtended": "0xUv+zFNIunVZ4bvazIZFoo3h0YmY95CgCnVGEb+4iw="
}
```

## Testy Utworzone

1. **test_minimal_eur.py** - Minimalny payload w EUR z hashExtended
2. **test_payment_automated.py** - Zaktualizowany o wszystkie zmiany

## Dalsze Kroki

1. **Przetestuj formularz** - Wyślij wygenerowany formularz do Fiserv
2. **Sprawdź odpowiedź** - Czy błąd "Unknown application error" nadal występuje?
3. **Jeśli błąd persystuje:**
   - Sklep testowy prawdopodobnie nie jest aktywny
   - Skontaktuj się z supportem Fiserv
   - Podaj: Store ID 760995999, przykładowe OID, czas testu

## Dane do Kontaktu z Supportem

```
Store ID: 760995999
Test Environment: https://test.ipg-online.com/connect/gateway/processing
Example Order ID: 6067bc19-0478-46b3-a151-2b16f3162269
Test Time: 2025-07-28 20:25:28 UTC
Currency Tested: EUR (978)
Timezone: Europe/Berlin
Hash Algorithm: HMACSHA256
Hash Field: hashExtended
Error: "Unknown application error" / "Transakcja nie może być zakończona powodzeniem"
```

## Podsumowanie

Wszystkie zalecane modyfikacje zostały wprowadzone:
- ✅ hashExtended zamiast hash
- ✅ Europe/Berlin jako strefa czasowa
- ✅ EUR (978) jako waluta testowa
- ✅ Usunięte polskie znaki diakrytyczne
- ✅ Dodany parametr paymentMethod

Jeśli błąd nadal występuje, problem leży po stronie konfiguracji merchant w systemie Fiserv.
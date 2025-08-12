# Fiserv - Działająca Konfiguracja

## ✅ KONTO JEST AKTYWNE!

Virtual Terminal działa, co potwierdza że konto testowe jest aktywne.

## Ważne Odkrycia z Virtual Terminal:

### 1. Terminal ID
- **Terminal ID: 80900000** (nie 760995999!)
- To może być kluczowa różnica

### 2. Wspierane Waluty
- **PLN działa** - widzisz PLN w Virtual Terminal
- Możesz testować z oryginalną walutą

### 3. Transaction Origin
- Virtual Terminal używa: **Mail Order/Telephone Order**
- Nasza integracja używa domyślnie **E-Commerce**

## Sugerowane Zmiany w Kodzie:

### A. Zaktualizuj Terminal ID (jeśli to konieczne)

```python
# W pliku .env dodaj:
FISERV_TERMINAL_ID=80900000

# Lub w fiserv_ipg_client.py możesz dodać pole:
form_fields['terminalID'] = '80900000'
```

### B. Wróć do PLN

```python
# fiserv_ipg_client.py - zmień z powrotem na PLN
'currency': '985',  # PLN
'timezone': 'Europe/Warsaw',  # Możesz spróbować wrócić do Warsaw
```

### C. Dodaj Transaction Origin

```python
# W form_fields dodaj:
'transactionOrigin': 'ECI'  # E-Commerce Indicator
# lub
'moto': 'false'  # Not Mail Order/Telephone Order
```

### D. Popraw Format Karty

Virtual Terminal pokazuje format: 416598XXXXXX2418
Upewnij się, że wysyłasz pełny numer karty bez spacji.

## Test z Poprawnymi Kartami

Karta z VT która nie zadziałała: 416598...2418

Użyj oficjalnych kart testowych Fiserv:
- **4005550000000019** (Visa)
- **5204740000001002** (Mastercard)

## Szybki Test

1. Zaktualizuj `currency` z powrotem na '985' (PLN)
2. Opcjonalnie dodaj `terminalID: 80900000`
3. Przetestuj ponownie

## Przykład Minimalnego Formularza z Terminal ID:

```html
<form method="POST" action="https://test.ipg-online.com/connect/gateway/processing">
    <input type="hidden" name="storename" value="760995999">
    <input type="hidden" name="terminalID" value="80900000">
    <input type="hidden" name="txntype" value="sale">
    <input type="hidden" name="timezone" value="Europe/Warsaw">
    <input type="hidden" name="txndatetime" value="2025:07:28-22:45:00">
    <input type="hidden" name="hash_algorithm" value="HMACSHA256">
    <input type="hidden" name="chargetotal" value="10.00">
    <input type="hidden" name="currency" value="985">
    <input type="hidden" name="checkoutoption" value="combinedpage">
    <input type="hidden" name="oid" value="TEST-VT-001">
    <input type="hidden" name="hashExtended" value="[calculated_hash]">
    <button type="submit">Test z Terminal ID</button>
</form>
```

## Wniosek

Konto jest aktywne! Problem leży w szczegółach konfiguracji. Najbardziej prawdopodobne przyczyny:
1. Brak lub błędny Terminal ID
2. Niewłaściwy format danych
3. Różnice między konfiguracją VT a IPG Connect
# Podsumowanie Problemu z Integracją Fiserv IPG Connect

## Problem
Integracja płatności z Fiserv IPG Connect zwraca błąd walidacji (`validationError`) zanim wyświetli stronę płatności.

## Dotychczasowe Odkrycia

### ✅ Co naprawiliśmy:
1. **Timezone**: Zmieniono z `Europe/Berlin` na `Europe/Warsaw`
2. **Timestamp**: Używamy czasu warszawskiego zamiast UTC (format: `YYYY:MM:DD-HH:MM:SS`)
3. **Hash**: Poprawna metoda HMAC-SHA256 z base64

### ❌ Co nadal nie działa:
Mimo poprawek, Fiserv zwraca błąd walidacji z komunikatem:
- "Your storename is not configured in the system"
- "The hash value is incorrect because it was generated incorrectly or your shared secret is wrong"
- "You are not permitted to perform this transaction at this time"

## Dane Testowe
```
Store ID: 760995999
Shared Secret: j}2W3P)Lwv
Gateway URL: https://test.ipg-online.com/connect/gateway/processing
```

## 10 Rozwiązań do Sprawdzenia

### 1. **Weryfikacja Shared Secret**
Problem: Shared secret może zawierać problematyczne znaki `}` i `)`
```python
# Test z różnymi wariantami escapowania
secrets_to_test = [
    "j}2W3P)Lwv",           # Oryginalny
    "j\\}2W3P\\)Lwv",       # Escaped
    "j%7D2W3P%29Lwv",       # URL encoded
    "j&#125;2W3P&#41;Lwv"  # HTML encoded
]
```

### 2. **Zmiana Algorytmu Hasha**
```python
# Spróbuj SHA1 zamiast SHA256
hash_algorithm = 'HMACSHA1'
# lub
hash_algorithm = 'SHA256'  # bez HMAC
```

### 3. **Testowanie Różnych Formatów Store ID**
```python
store_ids = [
    "760995999",      # Oryginalny
    "0760995999",     # Z zerem
    "76099599",       # Bez ostatniej cyfry
    "7609959999"      # Z dodatkową cyfrą
]
```

### 4. **Zmiana Kolejności Pól**
```python
# Test z różną kolejnością pól w formularzu
# Niektóre systemy wymagają specyficznej kolejności
form_fields = OrderedDict([
    ('txntype', 'sale'),
    ('storename', store_id),  # Storename jako drugie
    # ...
])
```

### 5. **Test z Różnymi Walutami**
```python
currencies = [
    ('985', 'PLN'),
    ('978', 'EUR'),
    ('840', 'USD'),
    ('826', 'GBP')
]
```

### 6. **Użycie Tokenizacji**
```python
# Zmiana checkoutoption
checkout_options = [
    'combinedpage',
    'simpleform',
    'classic',
    'payonly'
]
```

### 7. **Test z Innymi Typami Transakcji**
```python
txn_types = [
    'sale',
    'preauth',
    'postauth',
    'credit'
]
```

### 8. **Dodanie Pól Opcjonalnych**
```python
# Niektóre "opcjonalne" pola mogą być wymagane
form_fields['language'] = 'pl_PL'
form_fields['customerid'] = 'CUST123'
form_fields['invoicenumber'] = 'INV123'
form_fields['ponumber'] = 'PO123'
```

### 9. **Test z Różnymi Hashami**
```python
# Test różnych metod generowania hasha
def test_hash_methods():
    # Metoda 1: Tylko wartości
    hash_string = '|'.join(values)
    
    # Metoda 2: Klucz=wartość
    hash_string = '|'.join(f"{k}={v}" for k,v in fields)
    
    # Metoda 3: Klucz|wartość
    hash_string = '|'.join(f"{k}|{v}" for k,v in fields)
    
    # Metoda 4: Z shared secret na końcu
    hash_string = '|'.join(values) + '|' + shared_secret
```

### 10. **Zmiana User-Agent i Headers**
```python
headers_variants = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9'
    },
    {
        'User-Agent': 'Fiserv-IPG-Client/1.0',
        'Accept': '*/*'
    }
]
```

## Skrypt Testowy do Uruchomienia

```python
#!/usr/bin/env python3
"""
Kompleksowy test 10 różnych rozwiązań dla Fiserv
"""

import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import hmac
import hashlib
import base64
from collections import OrderedDict
import json

class FiservDebugger:
    def __init__(self):
        self.gateway_url = "https://test.ipg-online.com/connect/gateway/processing"
        self.results = []
    
    def test_solution(self, name, form_fields, description):
        """Test pojedynczego rozwiązania"""
        print(f"\n🧪 Test: {name}")
        print(f"   {description}")
        
        response = requests.post(
            self.gateway_url,
            data=form_fields,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            allow_redirects=False,
            timeout=10
        )
        
        success = 'validationError' not in response.headers.get('location', '')
        
        self.results.append({
            'name': name,
            'success': success,
            'status': response.status_code,
            'location': response.headers.get('location', '')[:100] if response.status_code in [302, 303] else None
        })
        
        if success:
            print(f"   ✅ SUKCES!")
        else:
            print(f"   ❌ Błąd walidacji")
        
        return success
    
    def run_all_tests(self):
        """Uruchom wszystkie testy"""
        # Tu implementacja wszystkich 10 testów
        pass

if __name__ == "__main__":
    debugger = FiservDebugger()
    debugger.run_all_tests()
```

## Pytania do Fiserv Support

1. Czy shared secret `j}2W3P)Lwv` jest poprawny? Czy znaki specjalne powinny być escapowane?
2. Czy store ID `760995999` jest aktywny w środowisku testowym?
3. Czy konto ma włączoną opcję "Allow URL override"?
4. Jaki dokładnie algorytm hashowania jest skonfigurowany dla tego store?
5. Czy są jakieś restrykcje IP lub domeny dla tego konta?
6. Czy możecie podać przykład działającego requesta dla tego store ID?
7. Jakie dokładnie pola są wymagane dla tego typu integracji?
8. Czy konto jest skonfigurowane dla "IPG Connect" czy innego typu integracji?
9. Czy timezone musi być zgodny z konfiguracją konta?
10. Czy są logi po waszej stronie pokazujące dokładny powód odrzucenia?

## Kontakt z Fiserv
Email: Sylwia.Golebiewska@fiserv.com (z poprzedniej korespondencji)
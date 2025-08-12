# 📧 Ostateczny Email do Supportu Fiserv

```
Temat: PILNE: ValidationError dla wszystkich transakcji - Store ID 760995999

Szanowni Państwo,

Otrzymuję błąd "validationError" dla WSZYSTKICH prób transakcji przez IPG Connect, niezależnie od konfiguracji.

KRYTYCZNA INFORMACJA:
Każda próba transakcji kończy się przekierowaniem na:
https://test.ipg-online.com/connect/redirectToFinalPage/validationError

To oznacza, że formularz jest ODRZUCANY na etapie walidacji, zanim w ogóle dojdzie do przetwarzania płatności.

DANE KONTA:
- Store ID: 760995999
- Terminal ID (z Virtual Terminal): 80900000
- Środowisko: Test/Sandbox
- Virtual Terminal: ✅ DZIAŁA (transakcje ręczne przechodzą bez problemu)
- IPG Connect: ❌ NIE DZIAŁA (wszystkie transakcje → validationError)

OTRZYMANE DANE DOSTĘPOWE:
- Store ID: 760995999
- Shared Secret: j}2W3P)Lwv
- API Key: xWdewnCcYTy8G0s4oS1r5GAOmcdVRYQn
- API Secret: aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG

WYKONANE TESTY (wszystkie zwracają validationError):

1. RÓŻNE SHARED SECRETS:
   - j}2W3P)Lwv (otrzymany)
   - aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG (API Secret)
   - c7dP/$5PBx (alternatywny)

2. RÓŻNE ALGORYTMY HASH:
   - HMACSHA256 + Base64
   - HMACSHA1 + Base64
   - HMACSHA256 + Hex

3. RÓŻNE POLA HASH:
   - hashExtended
   - hash
   - z/bez hash_algorithm

4. RÓŻNE KONFIGURACJE:
   - checkoutoption: combinedpage / classic
   - timezone: Europe/Berlin / Europe/Warsaw / UTC
   - currency: 985 (PLN) / 978 (EUR) / 840 (USD)
   - authenticateTransaction: false
   - paymentMethod: V / M

5. RÓŻNE ZESTAWY PÓL:
   - Pełny zestaw z URL-ami zwrotnymi
   - Minimalny zestaw (tylko wymagane pola)
   - Absolutne minimum (4 pola)

6. TEST Z PRZYKŁADOWYMI STORE ID Z DOKUMENTACJI:
   - Store ID: 10123456789 (secret: sharedsecret)
   - Store ID: 120995000 (secret: Test1234)
   - Store ID: 3344556677 (secret: mysecret)
   Wynik: Też otrzymuję validationError!

PRZYKŁADOWY REQUEST:
```
POST https://test.ipg-online.com/connect/gateway/processing
Content-Type: application/x-www-form-urlencoded

storename=760995999
txntype=sale
timezone=Europe/Berlin
txndatetime=2025:07:28-22:15:00
chargetotal=10.00
currency=985
checkoutoption=combinedpage
oid=TEST-20250728221500
hash_algorithm=HMACSHA256
hashExtended=[obliczony hash]
```

OBLICZANIE HASH:
Input string (sortowane alfabetycznie):
10.00|combinedpage|985|TEST-20250728221500|760995999|Europe/Berlin|2025:07:28-22:15:00|sale

Secret: j}2W3P)Lwv
Algorithm: HMAC-SHA256
Output (Base64): 7KgMGRxOxaqvbHNZDyeY4moau3EgL8i9ajIITwvd...

PRÓBY REST API:
- https://test.ipg-online.com/api/v1/* - wszystkie endpointy zwracają 404
- https://cert.api.firstdata.com/gateway/v2/payments - zwraca 401 (Unauthenticated)
- Payment Links API - nie jest dostępne

WNIOSKI:
1. Virtual Terminal działa = konto jest aktywne
2. Wszystkie transakcje IPG Connect → validationError
3. Problem występuje na etapie WALIDACJI formularza
4. Nawet przykładowe Store ID z dokumentacji nie działają

PILNE PYTANIA:
1. Czy Shared Secret "j}2W3P)Lwv" jest poprawny dla IPG Connect?
2. Czy IPG Connect jest w ogóle aktywny dla Store ID 760995999?
3. Dlaczego otrzymuję validationError nawet dla przykładowych Store ID z dokumentacji?
4. Czy istnieją dodatkowe wymagania konfiguracyjne dla konta testowego?
5. Czy mogę otrzymać przykład DZIAŁAJĄCEGO requesta dla mojego konta?

PROSZĘ O:
1. Potwierdzenie poprawnego Shared Secret dla IPG Connect
2. Weryfikację czy IPG Connect jest aktywny dla mojego Store ID
3. Przykład działającego requesta z poprawnymi danymi
4. Informację o ewentualnych brakujących krokach konfiguracyjnych

Przeprowadziliśmy ponad 30 różnych testów i każdy kończy się tym samym błędem validationError. 
Virtual Terminal działa bez zarzutu, więc problem jest specyficzny dla IPG Connect.

Z góry dziękuję za pilną pomoc.

Z poważaniem,
[Imię i nazwisko]
[Firma]
[Telefon]
[Email]

P.S. W załączeniu lista wszystkich wykonanych testów i ich wyniki.
```

## 📎 Załącznik: Lista Wykonanych Testów

### Pliki testowe utworzone podczas debugowania:
1. `test_payment_automated.py` - Standardowy test płatności
2. `test_minimal_payload.py` - Test z minimalnymi polami
3. `test_absolute_minimal.py` - Test absolutnie minimalny
4. `test_no_urls.py` - Test bez URL-i zwrotnych
5. `test_hash_variations.py` - Test różnych algorytmów hash
6. `test_alternative_secrets.py` - Test alternatywnych secretów
7. `test_rest_api.py` - Test REST API
8. `test_fiserv_dev_api.py` - Test różnych endpointów API
9. `test_firstdata_api.py` - Test FirstData API
10. `test_payment_links_api.py` - Test Payment Links
11. `test_example_store.py` - Test z przykładowymi Store ID
12. `test_additional_options.py` - Test dodatkowych opcji
13. `test_debug_validation.py` - Debug validation error
14. `test_with_env_secret.py` - Test z secretem z .env

### Wszystkie testy zwracają ten sam błąd:
```
https://test.ipg-online.com/connect/redirectToFinalPage/validationError
```

### Modyfikacje kodu wykonane zgodnie z dokumentacją:
- Usunięto pola: terminalID, transactionOrigin, paymentMethod
- Zmieniono timezone na Europe/Berlin
- Zmieniono pole hash na hashExtended
- Dodano obsługę GET dla webhook
- Usunięto polskie znaki z kodu

### Przetestowane kombinacje:
- 3 różne Shared Secrets
- 4 różne algorytmy hash
- 2 różne pola (hash/hashExtended)
- 3 różne strefy czasowe
- 3 różne waluty
- 2 różne checkoutoption
- Z i bez 3D Secure
- Z i bez URL-i zwrotnych
- Różne formaty timestamp
- Różne kolejności pól w hashu
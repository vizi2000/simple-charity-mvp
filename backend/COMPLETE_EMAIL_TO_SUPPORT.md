Subject: Pilna pomoc techniczna - Problem z integracją IPG Connect (Store ID: 760995999)

Szanowni Państwo,

Niniejszym zgłaszam problem z integracją płatności przez Fiserv IPG Connect na koncie testowym. Pomimo wielokrotnych prób i weryfikacji implementacji, nie jesteśmy w stanie przeprowadzić żadnej transakcji.

## Dane Konta
- **Store ID**: 760995999
- **Terminal ID**: 80900000
- **Środowisko**: Test/Sandbox
- **Typ Integracji**: IPG Connect (Form POST)

## Opis Problemu
Nie można przeprowadzić transakcji przez Fiserv IPG Connect. Transakcje nie docierają do etapu wprowadzania danych karty.

### Obserwowane Błędy:
1. **Combined Page**: `validationError` (błąd walidacji hash)
2. **Classic**: `Unknown application error` (brak konfiguracji)
3. **Virtual Terminal**: ✅ Działa poprawnie

## Kluczowe Informacje
- **Hash jest obliczany poprawnie** (HMAC-SHA256, Base64, sortowanie alfabetyczne, separator |)
- **Wszystkie testy implementacji** (50+ prób) potwierdzają poprawność kodu
- **Brak dostępu do Shared Secret** w Virtual Terminal
- **Combined Page jest skonfigurowana** w VT (widoczne metody płatności)
- **Classic Page nie jest skonfigurowana** w VT

## Przykładowy Request (Combined Page)
```
storename=760995999
txntype=sale
timezone=Europe/Berlin
txndatetime=2025:07:28-23:10:49
chargetotal=10.00
currency=985
checkoutoption=combinedpage
oid=TEST-20250728231049
hash_algorithm=HMACSHA256
hashExtended=[calculated_hash]
responseSuccessURL=https://yourapp.ngrok.app/api/payments/success
responseFailURL=https://yourapp.ngrok.app/api/payments/failure
transactionNotificationURL=https://yourapp.ngrok.app/api/payments/webhooks/fiserv
```

## Prośba o Wsparcie
1. **Podaj prawidłowy Shared Secret** dla IPG Connect (Store ID: 760995999)
2. **Potwierdź aktywację Combined Page** dla tego konta
3. **Sprawdź konfigurację konta** pod kątem wymaganych ustawień dla IPG Connect
4. **Podaj dokumentację** z dokładnymi wymaganiami dla tego konkretnego konta

## Dodatkowe Informacje
- Testy przeprowadzono z różnymi Shared Secrets (w tym z dokumentacji)
- Wszystkie możliwe konfiguracje pól formularza zostały przetestowane
- Problem nie występuje w Virtual Terminal, co potwierdza aktywność konta
- Transakcje w Virtual Terminal działają poprawnie

Proszę o pilną pomoc w rozwiązaniu tego problemu, który blokuje integrację płatności dla naszej aplikacji. Jest to kluczowe dla dalszego rozwoju naszego projektu.

Z poważaniem,
Zespół Deweloperski

**Dane kontaktowe:**
- Email: [Wpisz swój email]
- Telefon: [Wpisz numer telefonu]
- Projekt: Bramka płatnicza dla organizacji charytatywnych

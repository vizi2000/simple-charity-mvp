# Email do Fiserv - Końcowy Raport

## Temat: Re: Store ID 760995999 - Nadal błędy mimo poprawek

Dzień dobry,

Dziękuję za wcześniejszą odpowiedź. Po zastosowaniu wszystkich zaleceń i wykonaniu szczegółowych testów, mam następujące wyniki:

## 1. PROBLEM Z COMBINED PAGE

Zgodnie z Państwa zaleceniem użyłem `checkoutoption=combinedpage`, ale **to powoduje natychmiastowy błąd walidacji**.

Testy wykazały że:
- ✅ Minimalne pola (storename + chargetotal + currency) = DZIAŁA
- ✅ + txntype = DZIAŁA  
- ❌ + checkoutoption=combinedpage = NIE DZIAŁA (błąd walidacji)

**Wniosek: Combined Page NIE jest aktywna dla Store ID 760995999**

## 2. TRYB CLASSIC

Po zmianie na `checkoutoption=classic`:
- ✅ Przechodzi walidację (brak validationError)
- ✅ Hash jest akceptowany
- ❌ ALE nadal otrzymuję "nieznany błąd aplikacji"

## 3. PRZYKŁADOWE ID BŁĘDÓW

Z trybu Classic:
- 41a3c421-7de8-4725-b196-f18acd8d91dd
- [dodaj kolejne ID jeśli masz]

## 4. AKTUALNA KONFIGURACJA

```
storename: 760995999
timezone: Europe/Warsaw
currency: 985
checkoutoption: classic (combinedpage nie działa!)
shared secret: j}2W3P)Lwv
hash_algorithm: HMACSHA256
```

## 5. PYTANIA

1. **Dlaczego Combined Page nie działa** mimo że zalecili Państwo jej użycie?
   - Czy wymaga osobnej aktywacji?
   - Czy jest problem z konfiguracją?

2. **Dlaczego Classic daje "nieznany błąd aplikacji"**?
   - Hash przechodzi walidację
   - Więc problem jest gdzie indziej

3. **Co dokładnie oznacza błąd 41a3c421-7de8-4725-b196-f18acd8d91dd**?
   - Proszę o sprawdzenie w logach

4. **Czy Store ID 760995999 ma pełną aktywację IPG Connect**?
   - Virtual Terminal działa
   - Ale IPG Connect ma problemy

## 6. PROŚBA

Proszę o:
1. Sprawdzenie w logach co powoduje błąd 41a3c421-7de8-4725-b196-f18acd8d91dd
2. Aktywację Combined Page jeśli nie jest aktywna
3. LUB potwierdzenie że mam używać Classic i rozwiązanie problemu z błędem aplikacji
4. Przykład działającego requesta dla Store ID 760995999

Bez dokładnej informacji z logów nie jestem w stanie dokończyć integracji.

Z poważaniem,
[Imię i nazwisko]

---

## ZAŁĄCZNIK: Dokładny request który wysyłam (Classic)

```
POST https://test.ipg-online.com/connect/gateway/processing
Content-Type: application/x-www-form-urlencoded

storename=760995999
txntype=sale
timezone=Europe/Warsaw
txndatetime=2025:07:29-12:01:29
chargetotal=25.00
currency=985
checkoutoption=classic
oid=FINAL-TEST-20250729120129
hash_algorithm=HMACSHA256
hashExtended=OmQz8Q7Z8GnJIjD2SpwDfmA2guIidkwc/+V/H9K+qhI=
responseSuccessURL=https://yourapp.ngrok.app/api/payments/success
responseFailURL=https://yourapp.ngrok.app/api/payments/failure
transactionNotificationURL=https://yourapp.ngrok.app/api/payments/webhooks/fiserv
```
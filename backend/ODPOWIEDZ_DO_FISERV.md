# Odpowiedź do Fiserv Support

## Temat: Re: Store ID 760995999 - Nadal "Unknown application error"

Dzień dobry,

Dziękuję za odpowiedź. Niestety, mimo zastosowania WSZYSTKICH zaleceń, nadal otrzymuję błąd:

**"Unknown application error occurred. Please contact Support Team."**

## Zastosowane zmiany zgodnie z zaleceniami:

✅ **shared secret** = j}2W3P)Lwv  
✅ **timezone** = Europe/Warsaw  
✅ **currency** = 985  
✅ **checkoutoption** = combinedpage  

## Przykładowe ID błędnych transakcji:
- e61d03c9-9b13-405b-afff-0b66b064ef49
- [kolejne ID z testów]

## Dokładny request który wysyłam:

```
POST https://test.ipg-online.com/connect/gateway/processing
Content-Type: application/x-www-form-urlencoded

storename=760995999
txntype=sale
timezone=Europe/Warsaw
txndatetime=2025:07:29-11:38:53
chargetotal=10.00
currency=985
checkoutoption=combinedpage
oid=DEBUG-20250729113853
hash_algorithm=HMACSHA256
hashExtended=aDMsqleb5UDagk6UQ5PMtl5DPSwYh7yxYFT50wLj+dA=
```

## Obliczanie hash:

1. String do hasha (posortowany alfabetycznie):
   ```
   10.00|combinedpage|985|DEBUG-20250729113853|760995999|Europe/Warsaw|2025:07:29-11:38:53|sale
   ```

2. HMAC-SHA256 z secretem: j}2W3P)Lwv

3. Wynik w Base64: aDMsqleb5UDagk6UQ5PMtl5DPSwYh7yxYFT50wLj+dA=

## Testy wykonane:

1. **Z różnymi formatami txndatetime**:
   - 2025:07:29-09:33:56 (UTC)
   - 2025:07:29-11:33:56 (Warsaw time UTC+2)
   - Bez txndatetime
   - Wszystkie zwracają ten sam błąd

2. **Z URL-ami zwrotnymi i bez**:
   - Z responseSuccessURL, responseFailURL, transactionNotificationURL
   - Bez URL-i (używając VT)
   - Ten sam błąd

3. **Minimalna konfiguracja**:
   - Tylko storename, chargetotal, currency
   - Nadal błąd

## Virtual Terminal - działa poprawnie ✅

Transakcje ręczne w VT przechodzą bez problemu, więc konto jest aktywne.

## Pytania:

1. **Czy IPG Connect jest w pełni aktywowany dla Store ID 760995999?**
   - Virtual Terminal działa
   - Ale może IPG Connect wymaga osobnej aktywacji?

2. **Czy Combined Page jest poprawnie skonfigurowana dla IPG Connect?**
   - W VT widzę że Combined Page jest skonfigurowana
   - Ale może to nie wystarcza dla IPG Connect?

3. **Czy jest jakiś dodatkowy parametr którego brakuje?**
   - Może dla Store ID 760995999 są specjalne wymagania?

4. **Format txndatetime**:
   - Czy dla timezone=Europe/Warsaw powinienem wysyłać czas lokalny Warsaw czy UTC?
   - Jaki dokładnie format jest wymagany?

## Prośba:

1. Sprawdzenie w logach co dokładnie powoduje "Unknown application error" dla transakcji e61d03c9-9b13-405b-afff-0b66b064ef49

2. Potwierdzenie że IPG Connect jest w pełni aktywny dla tego Store ID

3. Przykład działającego requesta dla Store ID 760995999

Bez dokładnej informacji co jest przyczyną błędu, nie jestem w stanie dokończyć integracji.

Z poważaniem,
[Imię i nazwisko]
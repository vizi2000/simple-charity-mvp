# 📧 Email do Supportu Fiserv - Wersja Finalna

```
Temat: PILNE: Brak możliwości przeprowadzenia transakcji - Store ID 760995999

Szanowni Państwo,

Po wykonaniu ponad 50 testów i sprawdzeniu wszystkich ustawień w Virtual Terminal, transakcje przez IPG Connect nadal nie działają.

PROBLEM:
- Żadna transakcja nie dochodzi do strony wprowadzenia danych karty
- Combined Page: validationError (błąd walidacji formularza)
- Classic: "Unknown application error" (błąd aplikacji)
- Virtual Terminal: działa poprawnie (transakcje ręczne OK)

SPRAWDZONE USTAWIENIA W VIRTUAL TERMINAL:
✅ Online store integration → URL settings:
   - "Allow URLs to be overwritten" = ZAZNACZONE
   - Adresy URL = puste (używamy z formularza)

✅ Design adjustments:
   - Combined Page = SKONFIGUROWANA (widać metody płatności)
   - Classic = PUSTA (nie skonfigurowana)

❌ Brak dostępu do Shared Secret w Virtual Terminal
   - Nie ma takiej opcji w żadnym menu
   - Testowałem 3 różne secrety - żaden nie działa

TESTY WYKONANE:
1. Różne Shared Secrets:
   - j}2W3P)Lwv
   - c7dP/$5PBx  
   - aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG

2. Różne konfiguracje:
   - checkoutoption: classic / combinedpage
   - Waluty: PLN (985) / EUR (978) / USD (840)
   - Z i bez timezone, txndatetime
   - Różne formaty daty
   - Nawet bez hash (test desperacki)

3. Różne środowiska:
   - Internet mobilny → błąd
   - VPN (stałe IP) → ten sam błąd
   - ngrok URL-e → bez zmian

WYNIKI:
- Combined Page → ZAWSZE validationError
- Classic → ZAWSZE błąd aplikacji
- NIE WIDZĘ strony do wprowadzenia karty

WNIOSKI:
1. Shared Secret "j}2W3P)Lwv" jest nieprawidłowy
2. Lub IPG Connect nie jest w pełni aktywowany
3. Lub brakuje konfiguracji po stronie Fiserv

PROSZĘ O:
1. PRAWIDŁOWY Shared Secret dla IPG Connect
2. Sprawdzenie czy Store ID 760995999 ma aktywny moduł IPG Connect
3. Informację jakie moduły/usługi są nieaktywne
4. Przykład działającego requesta dla tego konta

DANE TECHNICZNE:
Store ID: 760995999
Terminal ID: 80900000
Environment: Test/Sandbox
Integration: IPG Connect (Form POST)

Bez prawidłowego Shared Secret lub aktywacji odpowiednich modułów nie mogę dokończyć integracji.

Z poważaniem,
[Imię i nazwisko]
[Firma]
[Telefon]
[Email]

P.S. Virtual Terminal działa bez zarzutu, problem dotyczy TYLKO integracji online (IPG Connect).
```

## 📎 Informacje dodatkowe dla supportu:

### Co dokładnie się dzieje:
1. Wysyłam formularz POST na https://test.ipg-online.com/connect/gateway/processing
2. Combined Page → Natychmiastowy redirect na /validationError
3. Classic → Redirect na stronę z błędem "Unknown application error"
4. NIE WIDZĘ formularza do wprowadzenia danych karty

### Przykładowe ID transakcji z błędami:
- 5060ddab-5851-44ad-8358-66440593731d
- 8e78c5ef-9dff-4bab-96d0-994ae7fdacb8

### Hash calculation (dla weryfikacji):
```
Input: 10.00|classic|985|TEST-123|760995999|Europe/Berlin|2025:07:28-22:00:00|sale
Secret: j}2W3P)Lwv
Algorithm: HMAC-SHA256
Output (Base64): [calculated hash]
```
# Virtual Terminal - Ustawienia URL

## 🔑 KLUCZOWE USTAWIENIE!

### "Overwrite Store URLs"
**☑️ ZAZNACZ TĘ OPCJĘ!**

Ta opcja pozwala na nadpisywanie URL-i z poziomu formularza Connect. Bez tego Fiserv może odrzucać transakcje zawierające własne URL-e powrotu.

## Zalecane Ustawienia:

### 1. Confirmation Page ("Thank You")
```
http://localhost:5174/platnosc/sukces
```
lub zostawić puste jeśli chcesz używać dynamicznych URL-i

### 2. Failure Page ("Sorry")  
```
http://localhost:5174/platnosc/blad
```
lub zostawić puste jeśli chcesz używać dynamicznych URL-i

### 3. Transaction Notification URL
```
https://77597ddbcc37.ngrok-free.app/api/webhooks/fiserv
```
lub zostawić puste jeśli używasz dynamicznych webhooków

### 4. ✅ Overwrite Store URLs
**MUSI BYĆ ZAZNACZONE!**

## Dlaczego to ważne?

Jeśli "Overwrite Store URLs" NIE jest zaznaczone:
- Fiserv ignoruje `responseSuccessURL` i `responseFailURL` z formularza
- Może to powodować błąd "Unknown application error"
- System oczekuje URL-i zdefiniowanych w VT, a nie w formularzu

## Kroki do wykonania:

1. Zaloguj się do Virtual Terminal
2. Znajdź Settings/Configuration → Online Store URL Settings
3. **ZAZNACZ "Overwrite Store URLs"**
4. Zapisz zmiany
5. Przetestuj ponownie minimalny formularz

## Alternatywne podejście:

Jeśli nie możesz zaznaczyć "Overwrite Store URLs", usuń z formularza:
- responseSuccessURL
- responseFailURL  
- transactionNotificationURL

I skonfiguruj stałe URL-e w Virtual Terminal.

## Test po zmianach:

Po zapisaniu ustawień w VT, użyj ponownie:
1. Minimalnego testu (test_absolute_minimal.py)
2. Jeśli zadziała, dodaj stopniowo więcej pól

## Inne ustawienia do sprawdzenia w VT:

- **Payment Methods** - czy Card jest włączone?
- **Currencies** - czy PLN (985) jest włączone?
- **API/Connect Settings** - czy jest sekcja konfiguracji dla Connect?
- **Hash Algorithm** - czy jest ustawione na HMACSHA256?

## Ważne!

Zmiany w Virtual Terminal mogą wymagać czasu na propagację. Po zapisaniu odczekaj 2-3 minuty przed testem.
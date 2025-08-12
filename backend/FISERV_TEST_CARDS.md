# 📳 Oficjalne Karty Testowe Fiserv

## ⚠️ WAŻNE: Karty testowe z dokumentacji

Na podstawie Twojej dokumentacji Fiserv, oficjalne karty testowe to:

### 1. **Visa**
- Numer: `4005550000000019`
- CVV: `111`
- Data ważności: `12/25` lub dowolna przyszła data

### 2. **Mastercard** 
- Numer: `5204740000001002`
- CVV: `111`
- Data ważności: `12/25` lub dowolna przyszła data

### 3. **Visa (alternatywna)**
- Numer: `4111111111111111`
- CVV: `111`
- Data ważności: dowolna przyszła data

## 🔍 Dlaczego może nie działać?

### 1. **Środowisko testowe może wymagać specyficznych kart**
- Niektóre karty mogą działać tylko z EUR/USD
- Niektóre mogą być tylko dla 'combinedpage'
- Niektóre mogą wymagać 3D Secure

### 2. **Problem z konfiguracją konta**
- Konto może nie mieć włączonej obsługi kart
- Może być tylko dla BLIK/przelewy
- Może wymagać dodatkowej aktywacji

### 3. **Karty mogą być przestarzałe**
- Dokumentacja może być nieaktualna
- Środowisko testowe mogło się zmienić

## 🧪 Co testować na stronie płatności Fiserv:

### Gdy dojdziesz do formularza karty:

1. **Najpierw spróbuj Visa:**
   ```
   Numer: 4005550000000019
   CVV: 111
   Data: 12/25
   Imię: Test User
   ```

2. **Jeśli nie działa, spróbuj Mastercard:**
   ```
   Numer: 5204740000001002
   CVV: 111
   Data: 12/25
   Imię: Test User
   ```

3. **Sprawdź komunikaty błędów:**
   - "Invalid card" = karta nieobsługiwana
   - "Transaction declined" = karta odrzucona
   - "3D Secure required" = wymaga dodatkowej autoryzacji

## 📝 Inne możliwe karty testowe (nieoficjalne):

### Visa:
- 4242424242424242
- 4000000000000002
- 4012888888881881

### Mastercard:
- 5555555555554444
- 5200828282828210
- 5105105105105100

## 🚨 Jeśli żadna karta nie działa:

To potwierdza że problem jest z konfiguracją konta, nie z integracją!

### Do emaila dla supportu dodaj:
```
PRÓBOWANE KARTY TESTOWE:
- Visa: 4005550000000019 - błąd: [jaki błąd]
- Mastercard: 5204740000001002 - błąd: [jaki błąd]
- Visa alt: 4111111111111111 - błąd: [jaki błąd]

Wszystkie karty z oficjalnej dokumentacji są odrzucane.
Czy konto testowe ma włączoną obsługę kart płatniczych?
```
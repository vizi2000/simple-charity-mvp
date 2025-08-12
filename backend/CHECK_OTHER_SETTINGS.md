# 🔍 Sprawdź pozostałe ustawienia

Skoro URL-e są OK, sprawdźmy inne opcje w "Online store integration":

## 1. **"Customize the design of your hosted payment forms"**
To kluczowa sekcja! Pokaż co tam jest:
- Czy payment forms są włączone?
- Jakie metody płatności są dostępne?
- Czy jest opcja wyboru między 'classic' a 'combinedpage'?

## 2. **"Add static text to your hosted payment forms"**
Mniej ważne, ale sprawdź czy nie ma tam:
- Ustawień bezpieczeństwa
- Ograniczeń walut
- Innych blokad

## 3. **Sprawdź też główne menu**
Czy jest gdzieś:
- **Security Settings** / **Hash Settings**
- **Currency Settings**
- **Payment Methods**
- **Store Configuration**

## 4. **W sekcji Administration → Fraud Settings**
Sprawdź:
- **Maximum Purchase Amount** - czy nie jest za niskie (np. 0 lub 1)?
- To może blokować transakcje

## 5. **Szukaj informacji o:**
- **Shared Secret** / **HMAC Key**
- **Supported Currencies**
- **Store Status** (Active/Test/Inactive)

## 🚨 Możliwe przyczyny które zostały:

1. **Shared Secret jest nieprawidłowy**
   - Może jest inny dla Connect niż ten który mamy
   - Może są spacje na początku/końcu

2. **Waluta PLN nie jest włączona**
   - Sprawdź listę dozwolonych walut

3. **Payment forms są wyłączone**
   - Muszą być włączone dla Connect

4. **Fraud settings blokują**
   - Za niski limit kwoty

Pokaż screenshoty z tych sekcji, szczególnie "Customize the design of your hosted payment forms"!
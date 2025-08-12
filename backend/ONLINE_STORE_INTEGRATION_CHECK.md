# ✅ ZNALEZIONE! Online Store Integration

To jest dokładnie to czego szukamy! Sprawdź te opcje:

## 1. **"Define the URLs for the integration with your online store"**

### 🔍 Co sprawdzić:
1. **Response Success URL** - czy jest ustawiony?
2. **Response Fail URL** - czy jest ustawiony?
3. **Transaction Notification URL** - czy jest?
4. **⚠️ WAŻNE: "Allow URL override"** lub **"Overwrite Store URLs"**
   - Ta opcja MUSI być zaznaczona!
   - Pozwala na przesyłanie URL-i w formularzu

### 📝 Jeśli są ustawione domyślne URL-e:
- Możesz je zostawić lub wyczyścić
- Ważne żeby zaznaczyć "Allow override"

## 2. **"Customize the design of your hosted payment forms"**

### 🔍 Sprawdź:
1. **Payment form status** - Enabled/Disabled?
2. **Supported payment methods**:
   - [ ] Credit/Debit Cards
   - [ ] BLIK
   - [ ] Inne
3. **Checkout type**:
   - [ ] Classic
   - [ ] Combined Page
   - [ ] Który jest włączony?

## 3. **Możliwe dodatkowe ustawienia:**

### A. Shared Secret / Security
- Może być w tej samej sekcji
- Szukaj "Security", "Hash", "HMAC", "Shared Secret"
- **Sprawdź czy Shared Secret = j}2W3P)Lwv**

### B. Currency Settings
- Supported currencies
- Sprawdź czy PLN (985) jest włączone

### C. Transaction Settings
- Minimum/Maximum amounts
- Allowed transaction types

## 4. **"Add custom fields to your hosted confirmation page"**

To potwierdza że masz HPP (Hosted Payment Page) = IPG Connect!

## 🚨 NAJWAŻNIEJSZE DO SPRAWDZENIA:

1. **W "Define URLs":**
   ```
   ✅ Zaznacz: "Allow transaction-specific response URLs" 
   lub "Allow URL override" lub podobne
   ```

2. **Status integracji:**
   - Czy jest włączona?
   - Czy są jakieś ostrzeżenia?

3. **Supported currencies:**
   - Czy PLN jest na liście?

4. **Payment methods:**
   - Czy karty są włączone?

## 💡 Jeśli znajdziesz problem:

### Scenariusz 1: Brak "Allow URL override"
- Zaznacz tę opcję i zapisz
- To może być przyczyną błędu!

### Scenariusz 2: PLN nie jest włączone
- Dodaj PLN do listy walut
- Lub testuj z EUR/USD

### Scenariusz 3: Karty nie są włączone
- Włącz Credit/Debit cards
- Sprawdź czy BLIK jest dostępny

## 📸 Zrób screenshot:
Jeśli możesz, pokaż co widzisz w tych ustawieniach!
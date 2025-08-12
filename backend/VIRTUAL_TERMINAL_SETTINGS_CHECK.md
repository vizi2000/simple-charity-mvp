# 🔍 Co sprawdzić w Virtual Terminal

## 1. **Główne ustawienia sklepu**

### A. Store Settings / Configuration
Szukaj sekcji:
- **Store Settings**
- **Terminal Configuration**
- **Merchant Settings**

Sprawdź:
- ✅ Store ID: 760995999 (potwierdź)
- ✅ Store Status: Active/Test
- ✅ Terminal ID: 80900000

### B. Payment Methods / Metody płatności
Szukaj:
- **Payment Methods**
- **Accepted Cards**
- **Payment Options**

Sprawdź czy włączone są:
- [ ] Visa
- [ ] Mastercard
- [ ] BLIK
- [ ] Cards (ogólnie)

## 2. **IPG Connect / Integration Settings**

### A. Szukaj sekcji:
- **IPG Connect**
- **Connect Settings**
- **HPP Configuration**
- **API Settings**
- **Integration**
- **E-commerce Settings**

### B. Sprawdź:
- [ ] Czy IPG Connect jest **AKTYWNY**?
- [ ] Czy jest osobna zakładka dla Connect?
- [ ] Status: Enabled/Disabled?

## 3. **Shared Secret / Security**

### A. Szukaj:
- **Security Settings**
- **Hash Configuration**
- **Shared Secret**
- **HMAC Settings**
- **API Credentials**

### B. Sprawdź:
- [ ] **Shared Secret** - czy jest taki sam jak używamy? (j}2W3P)Lwv)
- [ ] **Hash Algorithm** - HMACSHA256?
- [ ] Czy jest osobny secret dla Connect?

## 4. **Currency Settings / Waluty**

### A. Szukaj:
- **Currency Configuration**
- **Accepted Currencies**
- **Multi-Currency**

### B. Sprawdź czy włączone:
- [ ] PLN (985)
- [ ] EUR (978)
- [ ] USD (840)

## 5. **Checkout Options**

### A. Szukaj:
- **Checkout Configuration**
- **Payment Page Settings**
- **Hosted Page Options**

### B. Sprawdź:
- [ ] Czy jest opcja **classic**?
- [ ] Czy jest opcja **combinedpage**?
- [ ] Które są włączone?

## 6. **URL Configuration**

### A. Szukaj:
- **Response URLs**
- **Callback Settings**
- **Return URLs**

### B. Sprawdź:
- [ ] **"Allow URLs to be overwritten"** - czy jest zaznaczone?
- [ ] Czy są ustawione domyślne URL-e?

## 7. **Transaction Settings**

### A. Szukaj:
- **Transaction Configuration**
- **Processing Settings**
- **Risk Settings**

### B. Sprawdź:
- [ ] Minimum/Maximum amounts
- [ ] Allowed transaction types
- [ ] 3D Secure settings

## 8. **Logi / Historia**

### A. Szukaj:
- **Transaction Logs**
- **Error Logs**
- **Integration Logs**

### B. Znajdź nasze transakcje:
- ID: 5060ddab-5851-44ad-8358-66440593731d
- ID: 8e78c5ef-9dff-4bab-96d0-994ae7fdacb8

Sprawdź:
- Szczegóły błędu
- Reason code
- Detailed error message

## 🚨 NAJWAŻNIEJSZE:

### 1. **Status IPG Connect**
Czy w ogóle jest włączony? Może jest tylko Virtual Terminal aktywny.

### 2. **Shared Secret**
Czy jest dokładnie: `j}2W3P)Lwv`
Czy nie ma spacji na początku/końcu?

### 3. **Waluty**
Czy PLN jest włączone dla IPG Connect (nie tylko VT)?

### 4. **Checkout Options**
Czy 'classic' jest dostępne?

## 📸 Jeśli możesz:

Zrób screenshoty:
1. Głównych ustawień Store
2. Sekcji IPG Connect (jeśli jest)
3. Security/Hash settings
4. Currency configuration
5. Szczegółów błędnych transakcji

## 💡 Wskazówka:

Niektóre ustawienia mogą być w:
- **Administration** → **Store Settings**
- **Configuration** → **Payment Settings**
- **Setup** → **Integration Options**
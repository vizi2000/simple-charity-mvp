# 🔍 Gdzie szukać ustawień IPG Connect w Virtual Terminal

## 1. **Sprawdź główne menu**

Poszukaj tych opcji w menu:
- **Setup** / **Configuration**
- **Store Settings** / **Terminal Settings**
- **Integration** / **API Settings**
- **Payment Configuration**
- **E-Commerce** / **Online Payments**

## 2. **Możliwe lokalizacje ustawień Connect:**

### A. W menu głównym może być:
- **"Hosted Payment Page"**
- **"HPP Settings"**
- **"Connect Configuration"**
- **"Integration Settings"**
- **"Developer"** lub **"Developer Tools"**

### B. W Store/Terminal Settings szukaj:
- **Payment Methods**
- **Accepted Currencies**
- **Security Settings**
- **Hash/HMAC Configuration**

## 3. **Fraud Settings (które widzisz)**

Skoro masz Fraud Settings, sprawdź tam:
- **Maximum Purchase Amount** - czy nie jest za niskie?
- **Blocked IP addresses** - czy Twoje IP nie jest zablokowane?

## 4. **Transaction History**

Szukaj opcji:
- **Reports** / **Reporting**
- **Transaction Search**
- **Transaction History**
- **Search Transactions**

Znajdź transakcję o ID:
- `5060ddab-5851-44ad-8358-66440593731d`

I sprawdź szczegóły błędu.

## 5. **Jeśli nie ma opcji Connect/HPP**

To może oznaczać że:
1. **IPG Connect nie jest aktywny** dla tego konta
2. **Masz tylko dostęp do Virtual Terminal** (manual transactions)
3. **Potrzebujesz wyższego poziomu dostępu**

## 📝 Co zrobić:

### 1. Sprawdź Maximum Purchase Amount
W Fraud Settings → Set Maximum Purchase Amount
- Czy nie jest ustawione na 0 lub bardzo niskie?

### 2. Poszukaj w innych miejscach menu
Może być ukryte w:
- Podmenu
- Zakładkach
- Sekcji "More" lub "Advanced"

### 3. Sprawdź poziom użytkownika
W Manage Users sprawdź:
- Czy Twój użytkownik ma pełne uprawnienia?
- Czy jest opcja "API Access" lub "Developer Access"?

## 🚨 Jeśli nie znajdziesz ustawień IPG Connect:

**To potwierdza naszą diagnozę** - konto ma tylko Virtual Terminal, ale IPG Connect (API/HPP) nie jest aktywowany.

### Co wtedy:
1. **Kontakt z Fiserv** - poproś o aktywację IPG Connect
2. **Sprawdź umowę** - może trzeba dokupić tę usługę
3. **Administrator konta** - może tylko główny admin widzi te opcje

## 💡 Wskazówka:

Czasami ustawienia są w osobnym portalu:
- **Merchant Portal**
- **Developer Portal**
- **IPG Administration**

Może dostałeś osobny link do konfiguracji Connect?
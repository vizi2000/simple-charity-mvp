# 🛠️ Jak skonfigurować Classic Page

## Kroki konfiguracji:

### 1. **Wejdź do zakładki Classic**
W "Customize the design of your hosted payment forms" → kliknij zakładkę **"Classic"**

### 2. **Logo (opcjonalne)**
- Kliknij "Browse and select a file" w sekcji Header Area
- Możesz pominąć - nie jest wymagane

### 3. **Metody płatności (WAŻNE!)**
Classic może wymagać ręcznego włączenia metod płatności. Szukaj opcji:
- Payment Methods
- Accepted Cards
- Enable payment options

### 4. **Zapisz zmiany**
- Kliknij "Save Style"
- Poczekaj na potwierdzenie "Updated successfully"

## 🤔 Problem: Jeśli nie ma opcji dodania metod płatności w Classic

To może oznaczać że:
1. Classic nie jest dostępny dla tego konta
2. Wymaga osobnej aktywacji
3. Jest przestarzały i Fiserv wymusza Combined Page

## 🔍 WAŻNE: Znajdź Shared Secret!

### Gdzie szukać w Virtual Terminal:

1. **Reports/Reporting** → może być tam "API Settings"
2. **W głównym menu** szukaj:
   - Security
   - API Configuration
   - Developer Settings
   - Integration Keys
3. **Store Settings** (jeśli jest osobna sekcja)
4. **Help/Support** → może być dokumentacja z przykładami

### Może Shared Secret jest w:
- Emailu powitalnym od Fiserv
- Dokumentacji którą dostałeś
- Panelu developerskim (osobny portal?)

## 💡 Alternatywne rozwiązanie:

### Spróbuj bez hash (test desperacki):
Może hash nie jest wymagany w środowisku testowym?
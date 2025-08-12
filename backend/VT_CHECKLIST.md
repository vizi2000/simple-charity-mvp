# Virtual Terminal - Lista Kontrolna

## 🔍 Co dokładnie sprawdzić w Virtual Terminal:

### 1. **Sekcja Payment Configuration**
- [ ] Jakie metody płatności są włączone? (Card, BLIK, inne?)
- [ ] Czy jest osobna konfiguracja dla "Online/E-Commerce"?
- [ ] Czy jest różnica między "Virtual Terminal" a "Connect/HPP"?

### 2. **Sekcja Currencies**
- [ ] Czy PLN (985) jest na liście włączonych walut?
- [ ] Czy są jakieś ograniczenia kwotowe?

### 3. **Sekcja Security/Hash**
- [ ] Jaki algorytm hash jest ustawiony? (HMACSHA256?)
- [ ] Czy jest osobny klucz/secret dla Connect?
- [ ] Czy jest opcja "Require Hash" lub podobna?

### 4. **Sekcja API/Integration**
- [ ] Czy jest osobna sekcja dla "IPG Connect"?
- [ ] Czy są jakieś "Allowed IP addresses"?
- [ ] Czy jest "API Key" różny od tego co mamy?

### 5. **Transaction Settings**
- [ ] Czy są jakieś specjalne ustawienia dla transakcji?
- [ ] Minimalna/maksymalna kwota?
- [ ] Dozwolone typy transakcji (sale, preauth)?

### 6. **Store/Terminal Configuration**
- [ ] Czy Store ID w VT to na pewno 760995999?
- [ ] Czy jest może osobny "Connect Store ID"?
- [ ] Status sklepu (Active/Test/Inactive)?

## 🧪 Test w Virtual Terminal

Spróbuj wykonać transakcję RĘCZNIE w VT:
1. New Transaction → Sale
2. Amount: 10.00 PLN
3. Card: 4005550000000019
4. Process

**Czy ręczna transakcja działa?**
- TAK → Problem jest w integracji Connect
- NIE → Problem jest z kontem/konfiguracją

## 🔑 Możliwe przyczyny

### A. Różne środowiska
Virtual Terminal i Connect mogą używać różnych:
- Store ID
- Secret/klucz
- Endpoint URL

### B. Brak aktywacji Connect
Konto może mieć aktywny tylko Virtual Terminal, ale nie IPG Connect.

### C. Nieprawidłowy Shared Secret
Shared Secret dla Connect może być inny niż ten podany.

## 📝 Informacje do zebrania

W Virtual Terminal poszukaj i zapisz:
1. Dokładny Store ID (czy na pewno 760995999?)
2. Algorytm hash (czy na pewno HMACSHA256?)
3. Status Connect/HPP (czy jest włączony?)
4. Jakiekolwiek komunikaty/ostrzeżenia

## 🆘 Jeśli nic nie działa

Może być konieczne:
1. Kontakt z Fiserv Support
2. Poprosić o:
   - Potwierdzenie że Connect/HPP jest aktywny
   - Poprawny Shared Secret dla Connect
   - Przykładowy działający request

## 💡 Alternatywny test

Spróbuj zmienić w kodzie:
- `hash` zamiast `hashExtended`
- `HMACSHA1` zamiast `HMACSHA256` (jeśli jest opcja w VT)
- Inny timezone (UTC, Europe/Amsterdam)

## Debug Info dla Supportu

```
Environment: Test/Sandbox
Store ID: 760995999
Integration: IPG Connect (Form POST)
Error: "Unknown application error"
Hash Algorithm: HMACSHA256
Test Transaction IDs:
- MINIMAL-20250728230104
- NOURL-20250728230714
Virtual Terminal: Works OK
Connect/HPP: Fails with all configurations
```
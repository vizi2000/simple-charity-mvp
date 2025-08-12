# Backend Deployment - Poprawiona implementacja HMAC-SHA256

## Co zostało zmienione:

### 1. Algorytm hashowania
- **PRZED**: SHA256 z konkatenacją sharedSecret
- **PO**: HMAC-SHA256 z sharedSecret jako kluczem

### 2. Główna zmiana w pliku `app/routes/payments_working.py`:

```python
# STARA IMPLEMENTACJA (BŁĘDNA):
data_to_sign = f"{storename}{txndatetime}{chargetotal}{currency}{shared_secret}"
hash_value = hashlib.sha256(data_to_sign.encode()).hexdigest()

# NOWA IMPLEMENTACJA (POPRAWNA):
data_to_sign = f"{storename}{txndatetime}{chargetotal}{currency}"
hash_obj = hmac.new(
    shared_secret.encode('utf-8'),  # Klucz HMAC
    data_to_sign.encode('utf-8'),   # Dane do podpisania
    hashlib.sha256
)
hash_value = hash_obj.hexdigest()
```

### 3. Import modułu HMAC
Dodano: `import hmac` na początku pliku

## Pliki do zaktualizowania na serwerze:

1. `/home/wojtek/charity-mvp/backend/app/routes/payments_working.py`
   - Zastąp zawartość pliku zawartością z `payments_correct.py`

2. `/home/wojtek/charity-mvp/backend/main.py`
   - Upewnij się, że importuje `payments_working` (nie `payments_correct`)

## Jak wdrożyć:

### Opcja 1: Przez SSH (wymaga hasła)
```bash
# Skopiuj zaktualizowany plik
scp backend/app/routes/payments_working.py wojtek@192.168.100.159:/home/wojtek/charity-mvp/backend/app/routes/

# Zaloguj się na serwer
ssh wojtek@192.168.100.159

# Restart serwisu
cd /home/wojtek/charity-mvp/backend
sudo systemctl restart charity-backend
sudo systemctl status charity-backend
```

### Opcja 2: Ręczna aktualizacja
1. Zaloguj się na serwer jako użytkownik `vizi` (192.168.100.159)
2. Przejdź do: `/home/wojtek/charity-mvp/backend/app/routes/`
3. Edytuj plik `payments_working.py`
4. Zastąp funkcję `generate_hash_fiserv_method` nową implementacją
5. Dodaj `import hmac` na początku pliku
6. Restart serwisu: `sudo systemctl restart charity-backend`

## Weryfikacja:

Po wdrożeniu przetestuj:
1. Otwórz jeden z formularzy testowych HTML
2. Kliknij przycisk płatności
3. Powinno przekierować do Fiserv bez błędu walidacji

## Karty testowe Fiserv:
- **DEBIT**: 4410947715337430, 12/26, CVV: 287
- **BLIK**: 777777
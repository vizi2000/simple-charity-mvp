# ⚠️ WAŻNE: Dwie Różne Integracje Fiserv!

## 1. IPG Connect (Form POST) - TO UŻYWAMY
- **Dokumentacja:** IPG_IntegrationGuide_Connect_2023-4.pdf
- **Metoda:** HTML Form POST
- **URL:** https://test.ipg-online.com/connect/gateway/processing
- **Wymagane:**
  - Store ID: 760995999
  - Shared Secret: j}2W3P)Lwv
  - Hash: HMAC-SHA256
  - Pole: hashExtended lub hash

## 2. REST API - TO NIE UŻYWAMY (ale mamy klucze)
- **Dokumentacja:** https://docs.fiserv.dev/public/reference/payments-intro
- **Metoda:** REST API z JSON
- **Klucze:**
  - API Key: xWdewnCcYTy8G0s4oS1r5GAOmcdVRYQn
  - Secret Key: aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG

## 🔴 Problem!

Wygląda na to, że:
1. Mamy klucze do REST API
2. Ale próbujemy używać IPG Connect (Form POST)
3. To są RÓŻNE systemy!

## Co Teraz?

### Opcja A: Przejść na REST API
Skoro mamy działające klucze do REST API, możemy zmienić całą integrację.

### Opcja B: Uzyskać prawidłowe dane do IPG Connect
Shared Secret "j}2W3P)Lwv" może być nieprawidłowy lub Store ID jest inny.

## Test REST API

Sprawdźmy czy REST API działa z naszymi kluczami:
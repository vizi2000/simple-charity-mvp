#!/usr/bin/env python3
"""
Sprawdź który shared secret jest faktycznie używany
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Sprawdź zmienne środowiskowe
env_secret = os.getenv('FISERV_SHARED_SECRET')
print("="*60)
print("SPRAWDZENIE SHARED SECRET")
print("="*60)

print(f"\n1. Z zmiennej środowiskowej FISERV_SHARED_SECRET:")
print(f"   '{env_secret}'")

# Sprawdź co używa klient
from app.utils.fiserv_ipg_client import FiservIPGClient

client = FiservIPGClient()
print(f"\n2. Używany przez FiservIPGClient:")
print(f"   '{client.shared_secret}'")

# Porównaj z znanymi wartościami
known_secrets = {
    'j}2W3P)Lwv': 'Oryginalny z przykładu',
    'c7dP/$5PBx': 'Alternatywny z .env',
    'aGOkU61VoIl5AWApLL7avcCpIVZxVGG6jYGVQib8xuG': 'REST API Secret'
}

print(f"\n3. Analiza:")
for secret, desc in known_secrets.items():
    if client.shared_secret == secret:
        print(f"   ✅ Używamy: {desc}")
        print(f"      Secret: '{secret}'")
        break
else:
    print(f"   ⚠️ Nieznany secret: '{client.shared_secret}'")

print("\n" + "="*60)
print("WNIOSEK:")
print("="*60)

if client.shared_secret == 'c7dP/$5PBx':
    print("❌ UŻYWAMY ZŁEGO SECRETU!")
    print("   Aktualnie: 'c7dP/$5PBx' (z .env)")
    print("   Powinno być: 'j}2W3P)Lwv' (z przykładu Fiserv)")
    print("\n🔧 ROZWIĄZANIE:")
    print("   Zmień w .env na:")
    print("   FISERV_SHARED_SECRET=j}2W3P)Lwv")
elif client.shared_secret == 'j}2W3P)Lwv':
    print("✅ Secret jest poprawny")
    print("   Używamy: 'j}2W3P)Lwv'")
else:
    print(f"⚠️ Sprawdź czy secret '{client.shared_secret}' jest poprawny")
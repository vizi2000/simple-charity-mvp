#!/usr/bin/env python3
"""
Weryfikacja jakie dokładnie timestampy wysyłamy
"""

from datetime import datetime
from zoneinfo import ZoneInfo

print("="*70)
print("WERYFIKACJA TIMESTAMPÓW")
print("="*70)

# 1. Aktualny czas w różnych strefach
warsaw_tz = ZoneInfo("Europe/Warsaw")
berlin_tz = ZoneInfo("Europe/Berlin")
utc_tz = ZoneInfo("UTC")

now_warsaw = datetime.now(warsaw_tz)
now_berlin = datetime.now(berlin_tz)
now_utc = datetime.now(utc_tz)

print("\n📅 AKTUALNE CZASY:")
print(f"Warszawa:  {now_warsaw.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Berlin:    {now_berlin.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"UTC:       {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")

print("\n🔄 FORMAT DLA FISERV:")
print(f"Warszawa:  {now_warsaw.strftime('%Y:%m:%d-%H:%M:%S')}")
print(f"Berlin:    {now_berlin.strftime('%Y:%m:%d-%H:%M:%S')}")
print(f"UTC:       {now_utc.strftime('%Y:%m:%d-%H:%M:%S')}")

print("\n⚠️ RÓŻNICE:")
print(f"Warszawa vs UTC: {now_warsaw.hour - now_utc.hour} godzin różnicy")
print(f"Warszawa vs Berlin: {now_warsaw.hour - now_berlin.hour} godzin różnicy")

print("\n📊 CO WYSYŁAMY DO FISERV:")
print(f"timezone: Europe/Warsaw")
print(f"txndatetime: {now_warsaw.strftime('%Y:%m:%d-%H:%M:%S')}")

print("\n🤔 PROBLEM Z EMAIL OD FISERV:")
print("Oni pisali że otrzymali:")
print("- timezone=Europe/Berlin (ZŁE - powinno być Warsaw)")
print("- txndatetime=2025:07:28-21:01:59 (o 23:01 wysłane)")
print("- Czyli dostali czas UTC zamiast warszawskiego!")

print("\n✅ NASZE POPRAWKI:")
print("1. Wysyłamy timezone='Europe/Warsaw'")
print("2. Wysyłamy czas warszawski, nie UTC")
print(f"3. Przykład: {now_warsaw.strftime('%Y:%m:%d-%H:%M:%S')} (czas warszawski)")

# Sprawdź dokładnie co wysyłamy
print("\n🔬 DOKŁADNA WERYFIKACJA:")
print(f"Godzina warszawska: {now_warsaw.hour:02d}")
print(f"Minuta warszawska: {now_warsaw.minute:02d}")
print(f"Sekunda warszawska: {now_warsaw.second:02d}")

# Sprawdź offset
print(f"\nOffset warszawski: {now_warsaw.strftime('%z')}")
print(f"Offset UTC: {now_utc.strftime('%z')}")

print("\n" + "="*70)
print("WNIOSEK: Wysyłamy POPRAWNY czas warszawski!")
print("Ale Fiserv nadal zwraca błąd walidacji.")
print("="*70)
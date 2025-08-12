#!/bin/bash

echo "========================================="
echo "SPRAWDZANIE DOSTĘPNOŚCI ZEWNĘTRZNEJ"
echo "========================================="
echo ""

# Konfiguracja
PORT=8001
DDNS="borgtools.ddns.net"
PUBLIC_IP="194.181.240.37"

echo "1. Konfiguracja:"
echo "   - Port: $PORT"
echo "   - DDNS: $DDNS"
echo "   - Public IP: $PUBLIC_IP"
echo ""

echo "2. Sprawdzanie lokalnego serwera:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT | grep -q "200"; then
    echo "   ✅ Serwer działa lokalnie na porcie $PORT"
else
    echo "   ❌ Serwer nie odpowiada lokalnie"
fi
echo ""

echo "3. Sprawdzanie portów nasłuchujących:"
echo "   Porty nasłuchujące na $PORT:"
lsof -i :$PORT | grep LISTEN
echo ""

echo "4. URLs do testowania:"
echo "   - Lokalny: http://localhost:$PORT"
echo "   - DDNS: http://$DDNS:$PORT"
echo "   - IP: http://$PUBLIC_IP:$PORT"
echo ""

echo "5. Konfiguracja Firewall (macOS):"
echo "   Status firewall:"
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
echo ""

echo "========================================="
echo "WAŻNE KROKI DO WYKONANIA:"
echo "========================================="
echo ""
echo "1. Upewnij się, że port $PORT jest przekierowany w routerze:"
echo "   - Zaloguj się do panelu routera"
echo "   - Znajdź sekcję 'Port Forwarding' lub 'Virtual Server'"
echo "   - Dodaj regułę:"
echo "     * External Port: $PORT"
echo "     * Internal Port: $PORT"
echo "     * Internal IP: $(ipconfig getifaddr en0 2>/dev/null || echo "Twoje lokalne IP")"
echo "     * Protocol: TCP"
echo ""
echo "2. Testuj dostępność z zewnątrz:"
echo "   - Użyj telefonu (wyłącz WiFi)"
echo "   - Otwórz: http://$DDNS:$PORT"
echo "   - Lub poproś kogoś o test"
echo ""
echo "3. Adresy callback dla Fiserv:"
echo "   - Success URL: http://$DDNS:$PORT/payment-success"
echo "   - Fail URL: http://$DDNS:$PORT/payment-fail"
echo "   - Notification URL: http://$DDNS:$PORT/api/fiserv-notify"
echo ""
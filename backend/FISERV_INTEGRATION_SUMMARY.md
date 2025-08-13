Podsumowanie Integracji Płatności Fiserv – Wnioski i Dobre Praktyki
Proces integracji z bramką płatniczą Fiserv, choć z pozoru prosty, wymaga precyzyjnego przestrzegania reguł dotyczących bezpieczeństwa i formatowania danych. Poniższe podsumowanie zbiera wszystkie kluczowe lekcje i zasady, które wypracowaliśmy podczas sesji debugowania.

1. Główne Wyzwanie: Sygnatura Bezpieczeństwa (hash)
Cały proces debugowania koncentrował się wokół jednego, kluczowego elementu: poprawnego wygenerowania sygnatury bezpieczeństwa. Błąd w tym jednym polu powoduje, że bramka odrzuca całą transakcję. Przeszliśmy przez kilka etapów, aby dojść do prawidłowego rozwiązania:

Algorytm: Potwierdziliśmy, że wymagany jest HMAC-SHA256, a nie zwykły SHA256. Używa on sharedSecret jako tajnego klucza, a nie jako części danych.

Zakres Danych: Ustaliliśmy, że wszystkie parametry wysyłane w żądaniu (włącznie z transactionNotificationURL i opcjonalnymi polami jak bmail) muszą być uwzględnione w procesie hashowania.

Kolejność Danych: Odkryliśmy, że kluczowe jest alfabetyczne sortowanie parametrów według ich nazw (kluczy) przed połączeniem ich wartości w jeden ciąg.

Formatowanie Danych: Zweryfikowaliśmy, że wartości należy łączyć bezpośrednio, bez dodatkowych separatorów (jak |).

Kodowanie Wyniku: Finalnym przełomem było odkrycie, że surowy wynik funkcji HMAC-SHA256 musi być zakodowany w formacie Base64, a nie szesnastkowym (hex).

2. Złote Zasady Integracji z Fiserv
Na podstawie naszych doświadczeń, można sformułować pięć fundamentalnych zasad, których należy bezwzględnie przestrzegać:

Backend jest Królem Bezpieczeństwa:
Cała logika związana z tworzeniem transakcji, a zwłaszcza generowaniem hasha, musi odbywać się po stronie serwera (backendu). Nigdy nie umieszczaj sharedSecret w kodzie frontendowym (JavaScript, HTML).

Hashuj Wszystko, Co Wysyłasz:
Wszystkie parametry, które zamierzasz wysłać do Fiserv (z wyjątkiem samego pola hash), muszą zostać użyte do wygenerowania tego hasha. Pominięcie nawet jednego pola spowoduje błąd.

Sortuj Alfabetycznie Klucze:
Przed połączeniem wartości w jeden ciąg, posortuj wszystkie parametry alfabetycznie po ich nazwach (kluczach). To gwarantuje, że Twój serwer i serwer Fiserv pracują na identycznie uporządkowanych danych.

Używaj HMAC-SHA256 z Kluczem:
Zawsze używaj algorytmu HMAC-SHA256, gdzie sharedSecret pełni rolę tajnego klucza, a nie części danych do zahashowania.

Koduj Wynik w Base64:
Ostateczny, surowy wynik funkcji HMAC musi być zakodowany do formatu Base64, zanim zostanie umieszczony w polu hash formularza.

3. Kluczowe Uwagi Techniczne i Architektoniczne
Powiadomienia S2S to Jedyna Prawda: Przekierowanie użytkownika na stronę sukcesu (responseSuccessURL) nie jest potwierdzeniem płatności. Jedynym wiarygodnym źródłem informacji o statusie transakcji jest asynchroniczne powiadomienie Server-to-Server (S2S) wysłane na Twój transactionNotificationURL.

Testowanie Lokalne Wymaga Tunelu: Aby odbierać powiadomienia S2S na komputerze deweloperskim (za routerem), konieczne jest użycie narzędzia tworzącego tunel, takiego jak ngrok.

"Utwardzanie" Aplikacji jest Konieczne: Przed wdrożeniem produkcyjnym należy zaimplementować:

Walidację Danych Wejściowych: Sprawdzaj typy, formaty i zakresy danych (np. minimalna/maksymalna kwota).

Idempotentność Webhooka: Zabezpiecz endpoint S2S przed wielokrotnym przetworzeniem tego samego powiadomienia.

Szczegółowe Logowanie: Rejestruj kluczowe etapy i błędy, aby ułatwić przyszłą diagnostykę.

Stabilność Kodu: Zwracaj uwagę na subtelne błędy, takie jak modyfikowanie obiektu podczas iterowania po nim. Oddzielenie danych "do hashowania" od finalnego obiektu "do wysłania" zapewnia stabilność i przewidywalność działania.
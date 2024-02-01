# MyBankApp

Projekt realizowany w ramach zajęć z ochrony danych w systemach informatycznych na Politechnice Warszawskiej. MyBankApp to bezpieczna aplikacja bankowa zaprojektowana w celu ochrony danych użytkowników.


## 1. Funkcje projektu

1. **Logowanie przez wybrane znaki hasła:** Użytkownicy mogą zalogować się poprzez wybraną sekwencję znaków hasła.

2. **Wyświetlanie listy przelewów:** Aplikacja umożliwia przeglądanie historii przelewów.

3. **Podejrzenie danych wrażliwych:** Zabezpieczenie przed nieautoryzowanym dostępem do danych użytkowników.

4. **Wysłanie przelewu:** Możliwość dokonywania bezpiecznych przelewów.

5. **Zmiana hasła:** Użytkownicy mogą zmieniać hasło, przy czym wymagane jest silne hasło.

## 2. Zastosowane Zabezpieczenia

- **Walidacja danych wejściowych:** Dokładna walidacja wszystkich danych wprowadzanych przez użytkowników.

- **Wielokrotne hashowanie:** Zabezpieczenie przed atakami typu brute-force.

- **Blokowanie konta po nieprawidłowych próbach:** Ochrona przed próbami nieautoryzowanego dostępu.

- **Ogólna informacja o błędach:** Użytkownicy otrzymują czytelne komunikaty błędów.

- **Zmiana hasła na mocne hasło:** Zapewnienie, że nowe hasło spełnia wysokie standardy bezpieczeństwa.

- **Sesja z unikalnym ID i IP:** Kontrola zapytań oraz zabezpieczenie sesji poprzez unikalne identyfikatory.

- **Szyfrowana sesja:** Sesja zabezpieczona 128-bitowym hasłem.

- **Rotacja ID sesji:** Zmiana ID sesji po każdym żądaniu.

- **Automatyczne wylogowanie po minucie nieaktywności:** Dodatkowa warstwa bezpieczeństwa.

- **Przechowywanie danych sesji w bazie danych:** Bezpieczne przechowywanie informacji o sesji.

- **Hasło z 128-bitową solą:** Zwiększenie bezpieczeństwa hasła poprzez dodanie losowej soli.

- **Blokowanie globalne po 3 nieudanych próbach:** Ochrona przed atakami wielokrotnymi.

- **Zapamiętanie ostatniego loginu i jego prób:** Dodatkowe środki bezpieczeństwa.

## 3. Wymagania systemowe

- Zainstalowany [Docker](https://www.docker.com/)

## 4. Instalacja

1. Pobierz repozytorium:
    ```bash
    git clone https://github.com/ToMSoN28/MyBankApp
    ```

2. Uruchom kontener Docker:
    ```bash
    docker-compose up -d
    ```


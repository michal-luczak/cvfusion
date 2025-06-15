# SmartApply - Inteligentny Analizator Dopasowania CV

![Demo aplikacji SmartApply](./Zrzut%20ekranu%202025-06-16%20003718.png)
![Demo aplikacji SmartApply](./Zrzut%20ekranu%202025-06-16%20004020.png)

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SmartApply** to inteligentna aplikacja internetowa, która wykorzystuje moc dużych modeli językowych (Google Gemini) do automatycznej analizy i oceny dopasowania Twojego CV do konkretnej oferty pracy. Narzędzie oszczędza Twój czas, identyfikując kluczowe braki i dostarczając rekomendacje, które pomogą Ci dostosować aplikację i zwiększyć szanse na sukces.

## Kluczowe Funkcje

-   **Parsowanie CV z Plików PDF**: Automatycznie odczytuje i strukturyzuje kluczowe informacje z Twojego CV, takie jak doświadczenie, technologie i umiejętności.
-   **Analiza Ofert Pracy**: Przetwarza oferty pracy na dwa sposoby:
    -   **Z wklejonego tekstu**: Analizuje treść dowolnego ogłoszenia.
    -   **Z linku URL**: Automatycznie pobiera i analizuje treść ofert z popularnych portali, takich jak **LinkedIn** i **Pracuj.pl**.
-   **Ocena Dopasowania oparta na AI**: Generuje ocenę dopasowania w skali 0-100%, wskazując, jak dobrze Twój profil odpowiada wymaganiom.
-   **Identyfikacja Brakujących Umiejętności**: Wskazuje konkretne technologie i kompetencje, których brakuje w Twoim CV w kontekście danej oferty.
-   **Spersonalizowane Rekomendacje**: Dostarcza sugestie, co możesz podkreślić lub dodać w swoim CV, aby lepiej pasowało do ogłoszenia.
-   **Przyjazny Interfejs Użytkownika**: Prosta i intuicyjna obsługa dzięki frameworkowi Streamlit.

## Demo Aplikacji

 
*(Zastąp powyższy link własnym GIF-em lub zrzutem ekranu)*

## Jak to Działa? Architektura

Aplikacja opiera się na systemie trzech wyspecjalizowanych "agentów" AI, którzy współpracują ze sobą, aby dostarczyć kompleksową analizę:

1.  **ResumeParserAgent**:
    -   **Zadanie**: Otrzymuje surowy tekst wyekstrahowany z pliku PDF CV.
    -   **Wynik**: Przetwarza tekst za pomocą modelu Gemini, aby stworzyć ustrukturyzowany profil kandydata w formacie JSON (doświadczenie, technologie, umiejętności twarde i miękkie).

2.  **JobOfferAnalyzerAgent / JobMatchEvaluator**:
    -   **Zadanie**: Analizuje ofertę pracy. Działa w dwóch trybach:
        -   **Tryb Tekstowy (`JobOfferAnalyzerAgent`)**: Analizuje wklejony przez użytkownika tekst ogłoszenia, tworząc jego strukturyzowany opis w JSON.
        -   **Tryb URL (`JobMatchEvaluator`)**: Najpierw pobiera treść strony (web scraping) z podanego linku (LinkedIn/Pracuj.pl), oczyszcza ją z niepotrzebnych elementów (skrypty, stopki), a następnie przekazuje do analizy.
    -   **Wynik**: Ustrukturyzowane dane o ofercie pracy.

3.  **MatchEvaluatorAgent / JobMatchEvaluator**:
    -   **Zadanie**: Otrzymuje ustrukturyzowane dane z CV oraz z oferty pracy.
    -   **Wynik**: Porównuje oba zestawy danych, prosząc model Gemini o finalną ocenę: przyznanie punktacji (`score`), wylistowanie brakujących umiejętności (`missing_skills`) oraz sformułowanie rekomendacji (`recommendation`).

## Instalacja i Uruchomienie

Aby uruchomić projekt lokalnie, postępuj zgodnie z poniższymi krokami.

### Wymagania Wstępne

-   Python 3.9 lub nowszy
-   Konto Google i klucz API do Google Gemini. Klucz można uzyskać na [Google AI Studio](https://aistudio.google.com/app/apikey).

### Kroki Instalacji

1.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/twoja-nazwa-uzytkownika/SmartApply.git
    cd SmartApply
    ```

2.  **Utwórz i aktywuj wirtualne środowisko (zalecane):**
    ```bash
    # Dla Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Dla macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Zainstaluj wymagane biblioteki:**
    Utwórz plik `requirements.txt` o poniższej zawartości:
    ```
    streamlit
    google-generativeai
    PyPDF2
    requests
    beautifulsoup4
    ```
    A następnie zainstaluj go:
    ```bash
    pip install -r requirements.txt
    ```

### Uruchomienie Aplikacji

1.  Upewnij się, że pliki agentów (`job_offer_analyzer.py`, `resume_parser.py`, `match_evaluator.py`) znajdują się w folderze `agents/` w głównym katalogu projektu. Główny plik aplikacji powinien nazywać się `app.py`.

2.  Uruchom aplikację za pomocą polecenia Streamlit:
    ```bash
    streamlit run app.py
    ```

3.  Otwórz przeglądarkę internetową i przejdź pod adres `http://localhost:8501`.

4.  Wklej swój klucz Google Gemini API, załaduj CV i podaj ofertę pracy, aby rozpocząć analizę.

## Możliwe Ulepszenia

-   [ ] Zwiększenie odporności web scrapera na zmiany w strukturze stron LinkedIn i Pracuj.pl.
-   [ ] Dodanie wsparcia dla innych portali z ofertami pracy (np. Just Join IT, No Fluff Jobs).
-   [ ] Implementacja bazy danych (np. SQLite) do przechowywania historii analiz.
-   [ ] Generowanie sugestii konkretnych fragmentów do umieszczenia w CV.
-   [ ] Zapakowanie aplikacji do kontenera Docker w celu łatwiejszego wdrażania.
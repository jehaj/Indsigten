# Specifikationer: Indsigten

Dette dokument beskriver kravene til "Indsigten", et program til hurtig og intelligent søgning i PDF-dokumenter.

Så vidt som muligt skal programmet skrives modulært og følge design mønstre som f.eks. Strategy pattern, observer pattern, osv.. Det skal være nemt at tilføje/skifte en ny måde at generere vektorer (embeddings) af tekstbidder. Den visuelle brugergrænseflade skal bruge den anden funktionalitet som et bibliotek. PDF-håndtering og indeksering skal også virke uafhængigt af den visuelle brugergrænseflade, så vist man har løst til at lave en CLI, så kan det også lade sig gøre.

Der skal laves unit testing og programmet udvikles med Test-Driven Development. Der skal anvendes mocks og spies, hvor nødvendigt. Vi går efter et minimum af afhængigheder og vil helst implementere tingene selv, hvis det kan lade sig gøre. Vi skal selvfølgelig bruge moduler/biblioteker, hvor nødvendigt.

## Formål

At give brugeren mulighed for at finde information i store mængder PDF-filer ved at kombinere traditionel tekstsøgning (ripgrep) med moderne semantisk søgning (embeddings).

## Funktionelle krav

### 1. Brugergrænseflade (GUI)

* Programmet skal være en desktop-applikation bygget med **PySide6** (Qt for Python).
* Grænsefladen skal have:
  * Et søgefelt til både semantisk og præcis søgning.
  * En liste eller et område til visning af søgeresultater.
  * En menu eller knapper til at tilføje PDF-filer eller mapper til indekset.
  * Statusvisning (f.eks. "Indekserer...", "Søgning færdig").

### 2. PDF-håndtering og indeksering

* **Manuel kildevalg:** Brugeren vælger selv hvilke filer eller mapper, der skal inkluderes.
* **Tekst-udtrækning:** Brug `pdftotext` (fra poppler-utils) til at udtrække rå tekst fra PDF'erne.
* **Tekst-cache:** Den udtrukne tekst gemmes lokalt (f.eks. i en skjult mappe i brugerens hjemmemappe) for at muliggøre hurtig søgning med `ripgrep`.

### 3. Søgemaskine

* **Semantisk søgning:**
  * Brug **all-MiniLM-L6-v2** via `sentence-transformers`.
  * **Argumentation for modelvalg:**
    * **Effektivitet:** Denne model er ekstremt hurtig og fylder minimalt i hukommelsen (~80MB), hvilket gør den endnu mere velegnet til kørsel på bærbare computere med begrænsede ressourcer.
    * **Ydeevne:** Selvom den er lille, leverer den fremragende resultater for de fleste søgeopgaver og er en industristandard for letvægts semantisk søgning.
    * **Dimensioner:** Den bruger 384 dimensioner, hvilket reducerer både lagerplads og søgetid i forhold til større modeller.
  * Resultaterne gemmes i en **SQLite**-database.
  * Brug en ANN-metode (Approximate Nearest Neighbor) til hurtig genfinding af vektorer.
* **Præcis søgning:**
  * Kør `ripgrep` parallelt mod tekst-cachen for at finde eksakte tekststrenge.
* **Resultatvisning:**
  * Vis PDF-navn, sidenummer og et kort uddrag (snippet) af teksten.
  * Ranger resultaterne efter relevans (semantisk score kombineret med præcise match).

### 4. Visning af dokumenter

* Når brugeren klikker på et resultat, skal PDF'en åbnes i systemets standard PDF-viser.
* Programmet skal forsøge at sende parametre til PDF-viseren, så den åbner på det specifikke sidenummer.
  * Dette kan gøres ved at detektere de mest gængse PDF-visere (f.eks. Okular, Evince, Adobe Acrobat) og bruge deres respektive kommandolinje-argumenter (f.eks. `--page`).

## Tekniske specifikationer

* **Sprog:** Python 3.14+
* **GUI:** PySide6
* **Database:** SQLite (med vektorer gemt som BLOB eller via en udvidelse hvis muligt)
* **Værktøjer:**
  * `pdftotext` (til tekst-udtræk)
  * `ripgrep` (til hurtig søgning)
  * `EmbeddingGemma` (modellen til embeddings)
* **Miljøstyring:** `uv`

## Arkitektur

1. **Ingestion Layer:** Håndterer filvalg, kører `pdftotext`, splitter tekst i bidder/sider.
2. **Embedding Layer:** Sender bidder til EmbeddingGemma, gemmer resultater i SQLite.
3. **Search Layer:** Modtager forespørgsel, orkestrerer kald til SQLite (ANN) og `ripgrep`, fusionerer resultater.
4. **UI Layer:** PySide6-vindue der fungerer som bindeled mellem brugeren og de bagvedliggende lag.

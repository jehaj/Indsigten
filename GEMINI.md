# Projektinstruktioner: Indsigten

Dette dokument fungerer som den tekniske "grundlov" for projektet og indeholder bindende beslutninger om arkitektur og arbejdsgange.

## 1. Teknisk Kerne

* **Sprog:** Python 3.14+.
* **Layout:** "src-layout" (`src/indsigten`). Brug altid `PYTHONPATH=src` ved lokal kørsel af scripts.
* **Miljø:** `uv` er det primære værktøj til afhængigheder og miljøstyring.
* **GUI:** PySide6 følger objektorienterede principper for komponenter.

## 2. Arkitektoniske Beslutninger

* **Hybrid Søgning:** Implementeringen skal altid understøtte både semantisk (HNSW + SQLite) og præcis (ripgrep) søgning.
* **Optimeret Pipeline:**
  * Præcis søgning skal altid rapporteres først.
  * `EmbeddingModel` skal indlæses dovent (lazy loading) for at undgå blokering af programstart.
* **Persistens:** HNSW-indekset gemmes som en `.hnsw` fil ved siden af SQLite databasen.
* **Hashing:** Brug altid **SHA3-512** til identifikation af unikke filer.

## 3. Kodestandarder og Konventioner

* **TDD:** Skriv tests før kode. Brug `unittest` og `unittest.mock`.
* **Modularitet:** Hold lagene (Ingestion, Embedding, Search, UI) skarpt adskilte. Ingen direkte database-kald fra UI-laget.
* **Logging:** Brug Pythons standard `logging` modul. Sørg for at dæmpe støjende biblioteker (f.eks. `httpx`, `transformers`) ved programstart.

## 4. PDF-visning Workflow

* Dokumenter åbnes i systemets standardviewer.
* Der skal gøres et "best effort" forsøg på at sende sidenummer-argumenter (f.eks. `--page`) baseret på detekteret viewer (Okular, Evince, Adobe osv.).

# Indsigten

Lyn-hurtig og intelligent søgning i dine PDF-dokumenter ved hjælp af hybrid søgning: kombinerer præcisionen fra traditionel tekstsøgning med styrken fra semantisk AI.

## Kom hurtigt i gang

### 1. Forudsætninger

Sørg for at have følgende installeret på dit system:

* [uv](https://docs.astral.sh/uv/) (Python pakkehåndtering)
* `pdftotext` (fra `poppler-utils` pakken)
* `ripgrep` (`rg`)

### 2. Installation

Klon depotet og installer afhængigheder:

```bash
uv sync
```

### 3. Kørsel af søgning

Du kan bruge CLI-interfacet til at indeksere og søge med det samme:

```bash
PYTHONPATH=src uv run python3 main.py --dirs /sti/til/dine/pdf-mapper -- "din søgestreng"
```

---

## Hvorfor Indsigten?

* **Hybrid Søgning:** Programmet finder både præcise tekst-match (via `ripgrep`) og semantiske ligheder (via AI), så du finder det du leder efter, selvom du ikke husker de præcise ord.
* **Lyn-hurtig Respons:** Ved hjælp af en optimeret pipeline vises de præcise søgeresultater øjeblikkeligt, mens den tungere AI-model indlæses i baggrunden.
* **Ressource-effektiv:** Bruger den ekstremt effektive `all-MiniLM-L6-v2` model (~80MB RAM), hvilket gør at programmet kører problemfrit på bærbare computere med kun 8GB RAM.
* **Smart Indeksering:** Benytter **SHA2-256** hashing til at holde styr på dine filer. Kun nye eller ændrede filer indekseres, hvilket sparer tid og strøm.
* **Privatliv:** Alt kører lokalt på din maskine. Ingen data sendes til skyen.

## Udviklingsdetaljer

### Projektstruktur og `PYTHONPATH=src`

Dette projekt følger et moderne "src-layout". Det betyder, at kildekoden er isoleret i mappen `src/indsigten`.
For at køre programmet lokalt uden at installere det som en pakke, skal du prefixe din kommando med `PYTHONPATH=src`. Dette sikrer, at Python kan finde `indsigten` modulet korrekt.

### Teknisk Stak

* **Sprog:** Python 3.14+
* **Søgning:** HNSW (Hierarchical Navigable Small World) via `hnswlib` & `ripgrep`.
* **AI Model:** `all-MiniLM-L6-v2` via `sentence-transformers`.
* **Database:** SQLite.
* **GUI (Under udvikling):** PySide6 (Qt).

---
*Denne kode er skrevet af Gemini, men er blevet gennemset og kvalitetssikret af et menneske.*

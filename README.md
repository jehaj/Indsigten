# Indsigten

Find hurtigt det du leder efter i PDF-filer med semantisk søgning.

Håbet er at lave en hurtig python prototype og lave en ordentlig løsning i et kompileret sprog (såsom c++, go eller rust).

Læs mere om prorammet ved [spec.md](./spec.md).

## Udviklingsmiljø

Programmet skrives i python og der anvendes `uv` for at holde styr på python-miljøet.

### Hvorfor `PYTHONPATH=src`?

Projektet bruger en `src`-layout struktur, hvor kildekoden ligger i `src/indsigten`. Dette er en "best practice" i Python for at sikre, at testene kører mod den installerede pakke og ikke ved et uheld mod kildekoden direkte. Når man kører programmet lokalt uden at have installeret det som en pakke, skal man fortælle Python, at den skal lede efter moduler i `src` mappen.

## Brug af CLI

Du kan bruge kommandolinjen til at indeksere PDF-filer og søge i dem.

### Installation af afhængigheder

Sørg for at have `uv`, `pdftotext` (poppler-utils) og `ripgrep` installeret på dit system.
Kør derefter:

```bash
uv sync
```

### Kørsel af søgning

For at søge i en mappe med PDF-filer:

```bash
PYTHONPATH=src uv run python3 main.py --dirs demo -- "din søgestreng her"
```

### Parametre

* `--dirs`: En eller flere mapper der skal indekseres for PDF-filer.
* `--db`: (Valgfri) Sti til SQLite databasen (standard: `indsigten.db`).
* `--cache-dir`: (Valgfri) Sti til tekst-cachen brugt af ripgrep (standard: `.cache/indsigten` i din hjemmemappe).

Programmet bruger SHA3-512 hashing til at holde styr på hvilke filer der allerede er indekseret, så de ikke behandles flere gange.

---
*Denne kode er primært skrevet af Gemini (`Gemini CLI`), men er blevet gennemlæst og testet.*

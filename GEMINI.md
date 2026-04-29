# Projektinstruktioner: Indsigten

Dette dokument indeholder arkitektoniske beslutninger og arbejdsgange for Indsigten-projektet.

## Teknisk Stak
- **Sprog:** Python 3.14+
- **GUI Framework:** PySide6
- **Søgeteknologi:**
  - Semantisk: EmbeddingGemma (via sentence-transformers eller lignende).
  - Præcis: `ripgrep` på udtrukket tekst.
- **Dataopbevaring:** SQLite til metadata og embeddings.
- **PDF Behandling:** `pdftotext` (poppler-utils).

## Konventioner
- Brug `uv` til pakkehåndtering.
- Følg objektorienteret design til GUI-komponenter i PySide6.
- Adskil logik i lag som beskrevet i `spec.md` (Ingestion, Embedding, Search, UI).

## Arbejdsgang for PDF-visning
- Åbning af PDF'er skal ske via systemets standardviewer, men med forsøg på at hoppe til den korrekte side ved hjælp af kommandolinjeargumenter (f.eks. `--page`).

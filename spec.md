# Specifikationer: Indsigten

Dette dokument definerer de tekniske og funktionelle krav til "Indsigten".

## 1. Vision og Formål

Indsigten skal gøre det muligt for brugere at navigere i store mængder PDF-dokumenter med en hastighed og intelligens, der overgår standard søgeværktøjer. Dette opnås ved at fusionere **semantisk søgning** (forståelse af mening) med **præcis tekstsøgning** (ripgrep).

## 2. Designprincipper

* **Modulær Arkitektur:** Programmet skal følge anerkendte designmønstre (f.eks. Strategy og Observer). Logik og brugerflade skal være skarpt adskilt.
* **Performance Først:** Den præcise søgning skal prioriteres, og tunge ressourcer (som AI-modeller) skal indlæses dovent (lazy loading).
* **TDD (Test-Driven Development):** Alt kernefunktionalitet skal udvikles med tests først, understøttet af mocks og spies for at sikre isolation.
* **Minimalistiske Afhængigheder:** Vi foretrækker simple, effektive biblioteker og implementerer gerne logik selv, hvor det giver mening for at undgå "bloat".

## 3. Funktionelle Krav

### Brugergrænseflade (GUI)

* **Teknologi:** PySide6 (Qt for Python).
* **Funktioner:** Søgefelt til hybrid søgning, resultatoversigt med snippets, manuel styring af kilde-mapper og statusvisning for indeksering.

### Indeksering og Datahåndtering

* **Tekst-udtræk:** Brug af `pdftotext` til generering af råtekst.
* **Caching:** Udtræk gemmes lokalt for lynhurtig adgang via `ripgrep`.
* **Integritet:** Filer spores via **SHA2-256** hashes for at undgå unødig gen-indeksering.

### Søgemaskine (Hybrid)

* **Semantisk Del:**
  * Model: `all-MiniLM-L6-v2` (valgt for sin ekstreme effektivitet og lave hukommelsesaftryk på ~80MB).
  * Lager: Metadata og embeddings gemmes i **SQLite**.
  * Søgning: HNSW (Hierarchical Navigable Small World) algoritme for lynhurtig ANN (Approximate Nearest Neighbor) søgning.
* **Præcis Del:**
  * Værktøj: `ripgrep` køres parallelt mod tekst-cachen.

## 4. Teknisk Stak

* **Runtime:** Python 3.14+
* **Pakkehåndtering:** `uv`
* **Vektorsøgning:** `hnswlib`
* **PDF-behandling:** `poppler-utils` (`pdftotext`, `pdfinfo`)

## 5. Arkitektoniske Lag

1. **Ingestion Layer:** Håndterer filsystemet, hashing og tekst-ekstraktion.
2. **Embedding Layer:** Genererer vektorer og håndterer lazy loading af AI-modellen.
3. **Search Layer:** Orkestrerer hybrid-søgning og rangerer resultater.
4. **UI Layer:** PySide6-baseret grænseflade (eller CLI-interfacet).

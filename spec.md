# Specifikationer

Dette dokument indeholder kravene til programmet Indsigten.

Det skal bruge semantisk søgning (semantic search), så man kan søge og finde hvad man leder efter, så længe meningen er det samme uden det behøver at skrevet på samme måde. Dette kan gøres ved at bruge EmbeddingGemma, gemme resultaterne i en SQLite database og anvende Approximate Nearest Neighbor (ANN) søgning til at hurtigt finde det bagefter.

Derudover skal der også laves en tekst-cache, som kan søges i samtidigt for at undersøge om det man er interesseret i kan findes præcist. Dette kan gøres med `pdftotext'. Man kan så søge deri med 'ripgrep'. Alt dette skal ske automatisk og bag scenerne. Man søger i en generel grænseflade, som så vil vise hvilke PDFer indeholder, det man søger efter. Den skal vise hvilken side det er på, og hvis man klikker på resultatet, så skal den åbne PDFen på den side.

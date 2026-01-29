# Hybrid-Suche: Keyword + Semantik

Dieses Projekt zeigt einen **hybriden Suchansatz**, der **keyword-basierte Suche** (Ist-Zustand) mit **vektorbasierter semantischer Suche** (Neu/Konzept) kombiniert, um die Relevanz für natürlichsprachige Anfragen zu verbessern.

---
## Keyword vs. Semantik: Beispiele

### Problematisch für Keyword-Suche
- Sitzbezug für alle Autos mit einfacher Montage aus Tweed
- FS1Universal (0 Ergebnisse)
- JD Sitzbezug für Fahrersitz
- Stossdämpfer für John Deere
- Motorkettensäge Kinder
- Gardena Wandschlauchbox für den Garten

### Gut für Keyword-Suche
- Hevi Universalsitzbezug FS1
- FS1 Universal
- Wandschlauchbox
- Kettensäge Spielzeug
- John Deere Sitzbezug für Fahrersitz
- Stossdämpfer passend Fahrersitz für John Deere

> **Fazit:** Keyword-Suche scheitert oft bei langen, zusammengesetzten oder abgekürzten Anfragen. Semantische Suche kann die Konzepte erkennen.

TODO: BAKCUP with aussagen vom kristoph!
---

## 🧪 Beispiel Semantisches Verhalten

| Anfrage       | Passendes Dokument                   | Erklärung                                |
|---------------|-------------------------------------|-----------------------------------------|
| hello welt    | hi welt                              | ähnliche Grußbedeutung                   |
| handy kaufen  | mobiltelefon erwerben                | Synonyme werden erkannt                  |
| billiger Flug | kostengünstige Airline               | Kontextuelle Ähnlichkeit                 |
| Kinderschuhe  | Schuhe für Kinder                    | Domänenspezifische Semantik              |

> **Takeaway:** Semantische Suche erweitert die Trefferbasis, verbessert die Relevanz und reduziert Null-Ergebnisse.

---
## Funktionsweise der Hybrid-Suche
- Dokumente (Produkte) und Abfragen (Suchbegriffe) werden in **FastText-Embeddings** transformiert.
- **Kosinus-Ähnlichkeit** wird berechnet und mit der Solr-Keyword-Punktzahl kombiniert.
- Ergebnis: **konzeptbasiertes Matching**, selbst bei unterschiedlichen Keywords.
- **Vektoren** werden offline und asynchron erstellt → schnelles Indexing.
- Leichte Berechnung bei Abfragezeit.
- Nahtlose Integration in bestehende Solr-Setups, **kein Update nötig**.

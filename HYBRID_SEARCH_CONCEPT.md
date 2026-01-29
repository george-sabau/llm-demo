# 💡 Hybrid-Suche: Keyword + Semantik

Dieses Projekt zeigt einen **hybriden Suchansatz**, der **keyword-basierte Suche** mit **vektorbasierter semantischer Ähnlichkeit** kombiniert, um die Relevanz für natürlichsprachliche Anfragen zu verbessern.

- Dokumente (Produkte) und Anfragen (Suchanfragen) werden in **FastText-Embeddings** umgewandelt und mittels **Vektorbasierte-Ähnlichkeit** verglichen.  
  Das Ergebnis wird mit der Solr-Keyword-Punktzahl kombiniert, um ein **hybrides Ranking** zu erzeugen.  
  Dadurch ist ein **konzeptbasiertes Matching** möglich, selbst wenn die exakten Keywords unterschiedlich sind.
  - FastText-Embeddings: Worte/Tokens werden in N-Dimensionale-Vectoren umgewandelt und in einem Language-Model "abgelegt"
  - Vektorbasierte-Ähnlichkeit: Klassische Keyword-Suche liefert Treffer "nur" wenn Wortübereinstimmungen einem Muster/Matcher entsprechen und ignoriert hierbei den Kontext.
    Vektorbasierte-Ähnlichkeit hingegen arbeitet auf Vektor-Embeddings, die Wörter, Phrasen oder ganze Dokumente in numerische Repräsentationen umwandeln. Dabei werden semantische Ähnlichkeiten erfasst: Synonyme oder konzeptuell verwandte Begriffe werden auch ohne exakte Übereinstimmung erkannt. Dadurch ermöglicht die vektorbasierte Suche ein kontext- und bedeutungsorientiertes Matching, während klassische Keyword-Suche strikt literal bleibt.

- Die Vektorerstellung erfolgt **offline und asynchron**, wodurch das **Indexieren schnell** bleibt, während die Berechnung zur **Abfragezeit leichtgewichtig** ist. 
- Die Lösung lässt sich nahtlos in bestehende **Solr-Setups** integrieren, ohne dass ein **Solr-Update** erforderlich ist.

---
## 🧪 Keyword vs. Semantik: Beispiele

### Problematisch für Keyword-Suche
- Sitzbezug für alle Autos mit einfacher Montage aus Tweed
- FS1Universal (0 Ergebnisse)
- JD Sitzbezug für Fahrersitz
- Stossdämpfer für John Deere
- Motorkettensäge Kinder
- Gardena Wandschlauchbox für den Garten
- t-stück 20 mm (wenig Relevanz; kaum Teile mit 20 mm Durchmesser)

### Gut für Keyword-Suche
- Hevi Universalsitzbezug FS1 (genaue Übereinstimmung)
- FS1 Universal
- Wandschlauchbox
- Kettensäge Spielzeug
- John Deere Sitzbezug für Fahrersitz (genaue Übereinstimmung)
- Stossdämpfer passend Fahrersitz für John Deere (s.o.)

> **Fazit:** Keyword-Suche scheitert oft bei langen, zusammengesetzten oder abgekürzten Anfragen. Semantische Suche kann die Konzepte erkennen. Mit dem Hybriden-Suchansatz können wir
> die problematischen Such-Beispiele gut abdecken.
---

## 📌 Beispiel Semantisches Verhalten

| Anfrage       | Passendes Dokument                   | Erklärung                                |
|---------------|-------------------------------------|-----------------------------------------|
| hello welt    | hi welt                              | ähnliche Grußbedeutung                   |
| handy kaufen  | mobiltelefon erwerben                | Synonyme werden erkannt                  |
| billiger Flug | kostengünstige Airline               | Kontextuelle Ähnlichkeit                 |
| Kinderschuhe  | Schuhe für Kinder                    | Domänenspezifische Semantik              |

> **Fazit:** Semantische Suche erweitert die Trefferbasis, verbessert die Relevanz und reduziert Null-Ergebnisse.


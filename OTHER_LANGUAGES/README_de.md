# Chronolith

![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)

Chronolith ist eine kryptografische Integritätsschicht für die Dokumente, die die Absicht eines Projekts über KI-gestützte Sitzungen hinweg tragen. Es überführt Ihre kanonischen Dokumente in einen Merkle-Baum, hinterlegt eine signierte Referenz und bricht fail-closed ab, sobald der aktuelle Zustand nicht mehr dazu passt.

Es garantiert nicht, dass sich eine KI „erinnert". Es liefert einen überprüfbaren Nachweis darüber, was der vereinbarte Kontext *war*, und einen harten Stopp, wenn er abdriftet.

## Editionen

- **Lite**: minimale lokale Übergabe und signierte Zustandsprüfungen.
- **Pro**: der vollständige Wächter — Ed25519-signierte Referenzen, eine Append-only-Transparenzkette, Merkle-Inklusionsbeweise, Verschlüsselung, Schlüsselrotation und Bitcoin-Verankerung.
- **Omega**: RAG-orientierte kognitive Kartierung und Wirkungsanalyse.

## Installation

```bash
pip install chronolith
chronolith --help
```

Einzelne Pakete:

```bash
pip install chronolith-lite
pip install chronolith-pro
pip install chronolith-omega
```

## Überprüfbarer Nachweis

Ein Zustand dieses Projekts ist im **Bitcoin-Block 958484** verankert. Sie müssen weder diesem Repository noch seinem Autor vertrauen — prüfen Sie es selbst:

```bash
pip install "chronolith-pro[anchor]"
chronolith-pro verify-anchor --proof docs/evidence/ANCHOR_3647dd737ee8.json.ots
```

Was es beweist: Genau diese Daten existierten, bevor dieser Block geschürft wurde. Was es nicht beweist: wer sie geschrieben hat oder dass sie korrekt sind. Diese Grenzen sind dokumentiert, nicht verborgen.

## Produktgrenze

Chronolith ist die Python-Laufzeit und der Governance-Kern. Seneschal ist ein separates, herauslösbares Werkzeug für Token-Sparsamkeit und signierte Berechtigungen.

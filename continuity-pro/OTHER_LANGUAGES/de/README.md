# CONTINUITY LEGACY von Ethernium

`CONTINUITY LEGACY` ist ein eigenständiges Starter-Toolkit für die Erstellung von Projekten mit persistenter Kontinuität, kanonischem Speicher und einer wiederholbaren Übergabe (Handoff) zwischen Menschen und KI-Operatoren.

Dieses Toolkit stellt die Kontinuität an erste Stelle: Es bietet eine wiederverwendbare Disziplin für die Kontextpersistenz, die Dokumentenparitätsprüfung und eine gesteuerte Übergabe, ohne von einem externen Framework abhängig zu sein.

## Was enthalten ist
- eine minimale kanonische Speicherfläche
- ein Kontinuitäts-Bootstrap-Snapshot
- Dokumentenparitätsprüfungen
- Systemmitgliedschaftsprüfungen
- eine optionale externe Entwicklungsebene (z.B. `PROJECTDEV/`)
- ein strikter Kontinuitäts-Abschlussbefehl
- ein Bootstrapper zur Personalisierung der Vorlage

## Schnellstart

### 1. Der professionelle Weg (CLI) - EMPFOHLEN
Installieren Sie das globale CLI, um Projekte in einem Schritt zu initialisieren:

```powershell
pip install continuity-legacy
continuity-legacy init "Mein Projekt"
```

### 2. Manuelle Steuerung (Kopieren/Einfügen)
1. Kopieren Sie diesen Ordner in das Stammverzeichnis Ihres neuen Projekts.
2. Führen Sie den Bootstrapper aus:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Mein Projekt" --project-slug mein_projekt
```

3. Wenn Sie eine externe Kontinuitätsebene wünschen:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Mein Projekt" --project-slug mein_projekt --enable-external-docs
```

## Automatische Sicherheit (Continuity Guard)
Um sicherzustellen, dass das Projekt ohne manuellen Aufwand kohärent bleibt, enthält das Toolkit ein zweischichtiges Sicherheitssystem:

1. **Lokale Sicherheit (`pre-commit`)**: Standardmäßig installiert. Verwendet den "Soft"-Modus, um Sie während der Arbeit vor Abweichungen oder fehlenden Markierungen zu warnen, ohne Ihren kreativen Fluss zu blockieren.
2. **Grenzschutz (`pre-push`)**: Standardmäßig installiert. Verwendet den "Strict"-Modus, um den **Push zu GitHub zu blockieren**, wenn der Kontinuitätszyklus nicht zu 100% gültig ist.

## Kern-Dateien
- `PROJECT_CONTEXT.md`
- `STATE.json`
- `ROADMAP.md`
- `.continuity/LIVE_HANDOFF.md`
- `AGENT_START.md` (Datei, die einem neuen KI-Agenten übergeben wird)

---
**Weitere Einzelheiten finden Sie in den Anwendungsfällen und im Leitfaden zur Fehlerbehebung im Stammverzeichnis.**

# CONTINUITY LEGACY door Ethernium

`CONTINUITY LEGACY` is een onafhankelijke starter-toolkit voor het bouwen van projecten met persistente continuïteit, canoniek geheugen en een herhaalbare overdracht (handoff) tussen mensen en AI-operators.

Deze toolkit stelt continuïteit centraal: het biedt een herbruikbare discipline voor de persistentie van context, pariteitscontrole van documenten en een gecontroleerde overdracht zonder afhankelijk te zijn van externe frameworks.

## Wat dit bevat
- een minimaal canoniek geheugenoppervlak
- een continuïteits-bootstrap-snapshot
- document-pariteitscontroles
- systeem-lidmaatschapscontroles
- een optionele externe ontwikkellaag (bijv. `PROJECTDEV/`)
- een strikt continuïteits-afsluitingscommando
- een bootstrapper om het sjabloon te personaliseren

## Snelstart

### 1. De professionele manier (CLI) - AANBEVOLEN
Installeer de wereldwijde CLI om projecten in één stap te initialiseren:

```powershell
pip install continuity-legacy
continuity-legacy init "Mijn Project"
```

### 2. Handmatige controle (Kopiëren/Plakken)
1. Kopieer deze map naar de hoofdmap van je nieuwe project.
2. Voer de bootstrapper uit:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Mijn Project" --project-slug mijn_project
```

3. Als je een externe continuïteitslaag wilt:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Mijn Project" --project-slug mijn_project --enable-external-docs
```

## Automatische Beveiliging (Continuity Guard)
Om ervoor te zorgen dat het project coherent blijft zonder handmatige inspanning, bevat de toolkit een dubbellaags beveiligingssysteem:

1. **Lokale Bewaker (`pre-commit`)**: Standaard geïnstalleerd. Gebruikt de "Soft"-modus om je te waarschuwen voor afwijkingen of ontbrekende markeringen terwijl je werkt, zonder je creatieve flow te blokkeren.
2. **Grensbewaker (`pre-push`)**: Standaard geïnstalleerd. Gebruikt de "Strict"-modus om de **push naar GitHub te blokkeren** als de continuïteitscyclus niet 100% geldig is.

## Kernbestanden
- `PROJECT_CONTEXT.md`
- `STATE.json`
- `ROADMAP.md`
- `.continuity/LIVE_HANDOFF.md`
- `AGENT_START.md` (Bestand om aan een nieuwe AI-agent te overhandigen)

---
**Raadpleeg voor meer details de use cases en de gids voor probleemoplosser in de hoofdmap.**

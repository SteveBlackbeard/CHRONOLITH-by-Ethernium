# Continuity Legacy: Persistent Governance Layer 



`CONTINUITY LEGACY` è un kit di avvio indipendente progettato per costruire progetti con continuità persistente, memoria canonica e un passaggio di consegne (handoff) ripetibile tra umani e operatori IA.



Questo toolkit mette la continuità al primo posto: fornisce una disciplina riutilizzabile per la persistenza del contesto, la parità dei documenti e un trasferimento governato senza dipendere da alcun framework esterno.



## Cosa include

- una superficie di memoria canonica minima

- un'istantanea di avvio della continuità (snapshot)

- controlli di parità dei documenti

- controlli di appartenenza al sistema

- uno strato opzionale di sviluppo esterno (es: `PROJECTDEV/`)

- un comando di chiusura della continuità rigoroso

- un gestore di avvio (bootstrapper) per personalizzare il modello



## Avvio Rapido



### 1. La Via "Pro" (CLI) - RACCOMANDATO

Installa l'interfaccia a riga di comando globale per inizializzare i tuoi progetti in un unico passaggio:



```powershell

pip install continuity-legacy

continuity-legacy init "Il Mio Progetto"

```



### 2. Controllo Manuale (Copia/Incolla)

1. Copia questa cartella nella radice del tuo nuovo progetto.

2. Esegui il gestore di avvio:



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Il Mio Progetto" --project-slug il_mio_progetto

```



3. Se desideri uno strato di continuità esterna:



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Il Mio Progetto" --project-slug il_mio_progetto --enable-external-docs

```



## Protezione Automatica (Continuity Guard)

Per garantire che il progetto rimanga coerente senza sforzi manuali, il kit include un sistema di sicurezza a doppio strato:



1. **Guardia Locale (`pre-commit`)**: Installata di default. Utilizza la modalità "Soft" per avvisarti di derive o marcatori mancanti mentre lavori, senza bloccare il tuo flusso creativo.

2. **Guardia di Frontiera (`pre-push`)**: Installata di default. Utilizza la modalità "Strict" per **bloccare il push** verso GitHub se il ciclo di continuità non è valido al 100%.



## File Principali

- `PROJECT_CONTEXT.md`

- `STATE.json`

- `ROADMAP.md`

- `.continuity/LIVE_HANDOFF.md`

- `AGENT_START.md` (File da consegnare a un nuovo agente IA)



---

**Per maggiori dettagli, consulta i casi d'uso e la guida alla risoluzione dei problemi nella directory radice.**

---

| Guide | Link |
| :--- | :--- |
| [**Industrial Guide**](../../../docs/HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../../docs/HOW_TO_USE_IT.md) |
| [**Release Manifest**](../../../RELEASE_NOTES_MANIFEST.md) | [RELEASE_NOTES_MANIFEST.md](../../../RELEASE_NOTES_MANIFEST.md) |

---

---
*Continuity Legacy: Protecting the logical lineage of your software.*

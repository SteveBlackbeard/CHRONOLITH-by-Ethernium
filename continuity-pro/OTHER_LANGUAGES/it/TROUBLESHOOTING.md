# CONTINUITY LEGACY: Guida alla Risoluzione dei Problemi 🛠️



Qualcosa non torna? Non preoccuparti. Ecco le soluzioni ai problemi di continuità più comuni.



---



## 1. Il ciclo di parità fallisce (`doc_parity_check`) ✘



*   **Problema**: Ricevi un errore di "Document parity drift" che indica la mancanza di marcatori obbligatori.

*   **Causa**: Hai modificato un file (es. README o Handoff) e hai accidentalmente eliminato una riga che il sistema monitora per garantire la coerenza.

*   **Soluzione**:

    1.  Controlla il report in `outputs/continuity/continuity_cycle_report.json` per vedere quale "required_string" manca.

    2.  Aggiungi di nuovo il marcatore di parità nel documento.

    3.  Esegui nuovamente `python tools/continuity_legacy/run_continuity_cycle.py`.



---



## 2. Il Git Hook blocca il mio commit o push 🛡️



*   **Problema**: Git non ti permette di salvare o caricare modifiche.

*   **Causa**: Sei in modalità rigorosa (`--strict`) e il tuo `STATE.json` non corrisponde allo stato effettivo dei file.

*   **Soluzione**:

    1.  Esegui `python tools/continuity_legacy/continuity_status.py` per vedere la Dashboard della salute.

    2.  Sincronizza lo stato usando `python tools/continuity_legacy/run_continuity_cycle.py`.

    3.  Se si tratta di un'emergenza, puoi usare `git commit -m "msg" --no-verify` (non raccomandato!).



---



## 3. Il mio agente IA sembra "perso" o ignora il contesto 🤖



*   **Problema**: L'IA inizia a inventare cose o non sa dove si è interrotta la sessione precedente.

*   **Causa**: Non hai consegnato il pacchetto di avvio canonico o il file `LIVE_HANDOFF.md` è vuoto o non aggiornato.

*   **Soluzione**:

    1.  Assicurati di consegnare il file **`AGENT_START.md`** all'inizio della sessione.

    2.  Usa `python tools/continuity_legacy/continuity_suggest.py` per generare un buon riassunto di quanto accaduto e fornirlo all'IA.

    3.  Chiedi all'IA: *"Reconstruct your current state by reading the root STATE.json and tell me what your Next Exact Action is"* (Ricostruisci il tuo stato attuale leggendo lo STATE.json alla radice e dimmi qual è la tua prossima azione esatta).



---



## 4. Errore di "Security Warning" all'avvio ⚠️



*   **Problema**: Gli script Python lanciano un errore di sicurezza quando tentano di risolvere il percorso radice.

*   **Causa**: Stai cercando di eseguire gli script al di fuori di un repository valido di **CONTINUITY LEGACY**.

*   **Soluzione**:

    1.  Assicurati di essere nella radice del progetto.

    2.  Verifica che esista il file `continuity_legacy.json` o la cartella `.continuity`.

    3.  Se hai copiato il progetto manualmente, assicurati di eseguire prima `bootstrap_project.py`.



---



## 5. La Dashboard (`continuity_status`) mostra "Unknown" o "Skipped" ❓



*   **Problema**: Una sezione del sistema di salute non mostra dati.

*   **Causa**: Non hai completato un ciclo completo di continuità o la funzione "External Docs" è disabilitata.

*   **Soluzione**:

    1.  Esegui il ciclo: `python tools/continuity_legacy/run_continuity_cycle.py`.

    2.  Se utilizzi una cartella esterna (es. `MYPROJECTDEV`), assicurati di averla abilitata nel bootstrap con `--enable-external-docs`.

---
*Continuity Legacy: Protecting the logical lineage of your software.*

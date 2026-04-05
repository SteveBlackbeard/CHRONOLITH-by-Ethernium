# CONTINUITY LEGACY: Casi d'uso Reali 🚀

Questo documento descrive come applicare la filosofia della continuità in scenari del mondo reale.

---

## 1. Costruire Sistemi Complessi con l'IA 🏗️
Quando costruisci un'architettura con più componenti (es. database, API, frontend), l'IA spesso perde di vista le decisioni architettoniche passate.

*   **Utilizzare CONTINUITY LEGACY**: 
    -   Definisci l'architettura di base in `PROJECT_CONTEXT.md`. 
    -   Ogni volta che cambi lo schema del DB, registralo in `DECISIONS_LOG.md`.
    -   Al termine della sessione, `LIVE_HANDOFF.md` deve indicare quali tabelle sono state migrate e quali sono in sospeso.
*   **Vantaggio**: Il prossimo agente saprà *perché* hai scelto PostgreSQL invece di MongoDB e non proverà a cambiare la logica a metà percorso.

---

## 2. Agenti Cognitivi che "Imparano" 🧠
Un agente che lavora autonomamente ha bisogno di un luogo canonico per memorizzare ciò che ha imparato sull'ambiente.

*   **Utilizzare CONTINUITY LEGACY**: 
    -   L'agente usa `TIMELINE.md` per registrare le sue scoperte (es. "Errore 403 rilevato sull'API X; richiede token di tipo Y").
    -   L'agente aggiorna `STATE.json` per riflettere il suo nuovo livello di "conoscenza" del sistema.
*   **Vantaggio**: La continuità non riguarda solo il codice; riguarda la **conoscenza accumulata**.

---

## 3. Migrazione da strumenti di Memoria/RAG ⚡
Se usi già un database vettoriale (RAG) per la memoria della tua IA, potresti avere la sensazione che non sia abbastanza preciso per lo stato della sessione corrente.

*   **Utilizzare CONTINUITY LEGACY**: 
    -   Usa RAG per i "Dati Storici" o le "Librerie di Riferimento".
    -   Usa **CONTINUITY LEGACY** come lo **Stato Operativo Attivo**.
    -   Inserisci il `context_bootstrap_summary.json` nel System Prompt dell'agente.
*   **Vantaggio**: Passi da una memoria "statistica" (RAG) a una memoria "deterministica" (Continuità). L'IA avrà sempre ragione su ciò che sta accadendo *proprio ora*.

---

## 4. Lavoro Multi-Agente (Pair Programming Esteso) 🤝
Quando passi da una IA all'altra (es. programmazione con Claude ma rilascio con GPT-4).

*   **Utilizzare CONTINUITY LEGACY**: 
    -   Claude genera il `LIVE_HANDOFF.md`.
    -   GPT-4 legge `AGENT_START.md` all'ingresso.
    -   Entrambi convalidano la parità con il ciclo `--strict`.
*   **Vantaggio**: Il passaggio di consegne delle conoscenze è istantaneo e privo di errori umani. Non c'è "perdita di segnale" tra i modelli.

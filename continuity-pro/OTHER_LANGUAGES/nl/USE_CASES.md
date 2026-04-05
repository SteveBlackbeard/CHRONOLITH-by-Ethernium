# CONTINUITY LEGACY: Real-world Use Cases 🚀



Dit document beschrijft hoe je de filosofie van continuïteit kunt toepassen in real-world scenario's.



---



## 1. Complexe Systemen Bouwen met AI 🏗️

Bij het bouwen van een architectuur met meerdere componenten (bijv. database, API, frontend), verliest de AI vaak eerdere architecturale beslissingen uit het oog.



*   **CONTINUITY LEGACY Gebruiken**: 

    -   Definieer de basisarchitectuur in `PROJECT_CONTEXT.md`. 

    -   Elke keer dat je het database-schema wijzigt, noteer je dit in `DECISIONS_LOG.md`.

    -   Aan het einde van de sessie geeft `LIVE_HANDOFF.md` aan welke tabellen zijn gemigreerd en welke nog in de wacht staan.

*   **Voordeel**: De volgende agent weet *waarom* je PostgreSQL koos in plaats van MongoDB en zal niet proberen de logica halverwege het project te veranderen.



---



## 2. Cognitieve Agenten die "Leren" 🧠

Een agent die autonoom werkt heeft een canonieke plek nodig om op te slaan wat hij heeft geleerd over de omgeving.



*   **CONTINUITY LEGACY Gebruiken**: 

    -   De agent gebruikt `TIMELINE.md` om ontdekkingen vast te leggen (bijv. "Fout 403 gedetecteerd op API X; vereist token van type Y").

    -   De agent werkt `STATE.json` bij om zijn nieuwe niveau van "kennis" van het systeem te weerspiegelen.

*   **Voordeel**: Continuïteit gaat niet alleen over code; het gaat over **geaccumuleerde kennis**.



---



## 3. Migratie van Memory/RAG Tools ⚡

Als je al een vector-database (RAG) gebruikt voor het geheugen van je AI, heb je misschien het gevoel dat het niet nauwkeurig genoeg is voor de huidige sessiestatus.



*   **CONTINUITY LEGACY Gebruiken**: 

    -   Gebruik RAG voor "Historische Gegevens" of "Referentiebibliotheken".

    -   Gebruik **CONTINUITY LEGACY** als de **Actieve Operationele Status**.

    -   Injecteer de `context_bootstrap_summary.json` in de System Prompt van de agent.

*   **Voordeel**: Je stapt over van "statistisch" geheugen (RAG) naar "deterministisch" geheugen (Continuïteit). De AI heeft altijd gelijk over wat er *nu* gebeurt.



---



## 4. Multi-Agent Werk (Extended Pair Programming) 🤝

Wanneer je schakelt tussen verschillende AI's (bijv. programmeren met Claude maar implementeren met GPT-4).



*   **CONTINUITY LEGACY Gebruiken**: 

    -   Claude genereert de `LIVE_HANDOFF.md`.

    -   GPT-4 leest `AGENT_START.md` bij binnenkomst.

    -   Beiden valideren pariteit met de `--strict` cyclus.

*   **Voordeel**: De overdracht van kennis is onmiddellijk en vrij van menselijke fouten. Er is geen "signaalverlies" tussen de modellen.

---
*Continuity Legacy: Protecting the logical lineage of your software.*

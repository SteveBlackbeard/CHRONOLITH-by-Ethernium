# CHRONOLITH: Gids voor Probleemoplossing 🛠️



Klopt er iets niet? Geen paniek. Hier zijn de oplossingen voor veelvoorkomende continuïteitsproblemen.



---



## 1. Pariteitscontrole Mislukt (`doc_parity_check`) ✘



*   **Probleem**: Je krijgt de foutmelding "Document parity drift" die aangeeft dat verplichte markeringen ontbreken.

*   **Oorzaak**: Je hebt een bestand bewerkt (bijv. README of Handoff) en per ongeluk een regel verwijderd die het systeem bewaakt om de consistentie te waarborgen.

*   **Oplossing**:

    1.  Bekijk het rapport in `outputs/chronolith/chronolith_cycle_report.json` om te zien welke "required_string" ontbreekt.

    2.  Voeg de pariteitsmarkering weer toe aan het document.

    3.  Voer `python tools/chronolith/run_chronolith_cycle.py` opnieuw uit.



---



## 2. Git Hook Blokkeert Mijn Commit of Push 🛡️



*   **Probleem**: Git staat je niet toe om wijzigingen op te slaan of te uploaden.

*   **Oorzaak**: Je bevindt je in de strikte modus (`--strict`) en je `STATE.json` komt niet overeen met de werkelijke staat van de bestanden.

*   **Oplossing**:

    1.  Voer `python tools/chronolith/chronolith_status.py` uit om het dashboard voor gezondheidscontrole te bekijken.

    2.  Synchroniseer de status met `python tools/chronolith/run_chronolith_cycle.py`.

    3.  In geval van nood kun je `git commit -m "msg" --no-verify` gebruiken (niet aanbevolen!).



---



## 3. Mijn AI-agent Lijkt "Verdwaald" of Negeert Context 🤖



*   **Probleem**: De AI begint dingen te verzinnen of weet niet waar de vorige sessie eindigde.

*   **Oorzaak**: Je hebt het canonieke starterspakket niet overhandigd of `LIVE_HANDOFF.md` is leeg of verouderd.

*   **Oplossing**:

    1.  Zorg ervoor dat je het bestand **`AGENT_START.md`** aan het begin van de sessie overhandigt.

    2.  Gebruik `python tools/chronolith/chronolith_suggest.py` om een goede samenvatting te genereren van wat er is gebeurd en geef deze aan de AI.

    3.  Vraag de AI: *"Reconstruct your current state by reading the root STATE.json and tell me what your Next Exact Action is"* (Reconstrueer je huidige staat door de hoofd-STATE.json te lezen en vertel me wat je volgende exacte actie is).



---



## 4. Foutmelding "Security Warning" bij Opstarten ⚠️



*   **Probleem**: Python-scripts geven een beveiligingsfout bij het proberen op te lossen van het hoofdpad.

*   **Oorzaak**: Je probeert de scripts uit te voeren buiten een geldige **CHRONOLITH**-repository.

*   **Oplossing**:

    1.  Zorg ervoor dat je je in de hoofdmap van het project bevindt.

    2.  Controleer of het bestand `chronolith.json` of de map `.chronolith` bestaat.

    3.  Als je het project handmatig hebt gekopieerd, zorg er dan voor dat je eerst `bootstrap_project.py` uitvoert.



---



## 5. Dashboard (`chronolith_status`) Toont "Unknown" of "Skipped" ❓



*   **Probleem**: Een sectie van het gezondheidssysteem toont geen gegevens.

*   **Oorzaak**: Je hebt nog geen volledige continuïteitscyclus voltooid of de functie "External Docs" is uitgeschakeld.

*   **Oplossing**:

    1.  Voer de cyclus uit: `python tools/chronolith/run_chronolith_cycle.py`.

    2.  Als je een externe map gebruikt (bijv. `MYPROJECTDEV`), zorg er dan voor dat je deze hebt ingeschakeld in de bootstrap met `--enable-external-docs`.

---
*Chronolith: Protecting the logical lineage of your software.*

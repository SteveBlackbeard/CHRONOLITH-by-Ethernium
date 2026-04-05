# CONTINUITY LEGACY: Leitfaden zur Fehlerbehebung 🛠️

Etwas passt nicht zusammen? Keine Panik. Hier sind die Lösungen für gängige Kontinuitätsprobleme.

---

## 1. Paritätszyklus schlägt fehl (`doc_parity_check`) ✘

*   **Problem**: Sie erhalten eine Fehlermeldung "Document parity drift", die auf fehlende Pflichtmarkierungen hinweist.
*   **Ursache**: Sie haben eine Datei bearbeitet (z. B. README oder Handoff) und versehentlich eine Zeile gelöscht, die das System zur Sicherstellung der Konsistenz überwacht.
*   **Lösung**:
    1.  Prüfen Sie den Bericht in `outputs/continuity/continuity_cycle_report.json`, um zu sehen, welcher "required_string" fehlt.
    2.  Fügen Sie die Paritätsmarkierung wieder in das Dokument ein.
    3.  Führen Sie `python tools/continuity_legacy/run_continuity_cycle.py` erneut aus.

---

## 2. Git Hook blockiert meinen Commit oder Push 🛡️

*   **Problem**: Git lässt Sie keine Änderungen speichern oder hochladen.
*   **Ursache**: Sie befinden sich im strikten Modus (`--strict`), und Ihre `STATE.json` stimmt nicht mit dem tatsächlichen Zustand der Dateien überein.
*   **Lösung**:
    1.  Führen Sie `python tools/continuity_legacy/continuity_status.py` aus, um das Health Dashboard zu sehen.
    2.  Synchronisieren Sie den Status mit `python tools/continuity_legacy/run_continuity_cycle.py`.
    3.  Im Notfall können Sie `git commit -m "msg" --no-verify` verwenden (Nicht empfohlen!).

---

## 3. Mein KI-Agent wirkt "verloren" oder ignoriert den Kontext 🤖

*   **Problem**: Die KI fängt an, Dinge zu erfinden, oder weiß nicht, wo die vorherige Sitzung aufgehört hat.
*   **Ursache**: Sie haben das kanonische Starterpaket nicht übergeben oder `LIVE_HANDOFF.md` ist leer/veraltet.
*   **Lösung**:
    1.  Stellen Sie sicher, dass Sie die Datei **`AGENT_START.md`** zu Beginn der Sitzung übergeben.
    2.  Verwenden Sie `python tools/continuity_legacy/continuity_suggest.py`, um eine gute Zusammenfassung der bisherigen Ereignisse zu erstellen und der KI zu übergeben.
    3.  Fragen Sie die KI: *"Reconstruct your current state by reading the root STATE.json and tell me what your Next Exact Action is"* (Rekonstruiere deinen aktuellen Zustand durch Lesen der Stammdatei STATE.json und nenne mir deinen nächsten exakten Schritt).

---

## 4. "Security Warning"-Fehler beim Start ⚠️

*   **Problem**: Python-Skripte werfen einen Sicherheitsfehler beim Versuch, den Stammpfad aufzulösen.
*   **Ursache**: Sie versuchen, die Skripte außerhalb eines gültigen **CONTINUITY LEGACY**-Repositorys auszuführen.
*   **Lösung**:
    1.  Stellen Sie sicher, dass Sie sich im Projektstammverzeichnis befinden.
    2.  Prüfen Sie, ob die Datei `continuity_legacy.json` oder der Ordner `.continuity` existiert.
    3.  Wenn Sie das Projekt manuell kopiert haben, führen Sie unbedingt zuerst `bootstrap_project.py` aus.

---

## 5. Dashboard (`continuity_status`) zeigt "Unknown" oder "Skipped" ❓

*   **Problem**: Ein Bereich des Gesundheitssystems zeigt keine Daten an.
*   **Ursache**: Sie haben noch keinen vollständigen Kontinuitätszyklus abgeschlossen oder die Funktion "External Docs" ist deaktiviert.
*   **Lösung**:
    1.  Führen Sie den Zyklus aus: `python tools/continuity_legacy/run_continuity_cycle.py`.
    2.  Wenn Sie einen externen Ordner verwenden (z. B. `MYPROJECTDEV`), stellen Sie sicher, dass Sie diesen beim Bootstrap mit `--enable-external-docs` aktiviert haben.

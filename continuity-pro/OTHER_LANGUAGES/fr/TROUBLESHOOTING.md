# CONTINUITY LEGACY: Guide de Dépannage (Troubleshooting) 🛠️

Quelque chose ne correspond pas ? Pas de panique. Voici les solutions aux problèmes de continuité courants.

---

## 1. Le cycle de parité échoue (`doc_parity_check`) ✘

*   **Problème** : Vous recevez une erreur de "Document parity drift" indiquant des marqueurs obligatoires manquants.
*   **Cause** : Vous avez édité un fichier (ex: README ou Handoff) et avez accidentellement supprimé une ligne que le système surveille pour assurer la cohérence.
*   **Solution** :
    1.  Vérifiez le rapport dans `outputs/continuity/continuity_cycle_report.json` pour voir quelle "required_string" manque.
    2.  Ajoutez le marqueur de parité à nouveau dans le document.
    3.  Exécutez `python tools/continuity_legacy/run_continuity_cycle.py` à nouveau.

---

## 2. Le Git Hook bloque mon commit ou mon push 🛡️

*   **Problème** : Git ne vous laisse pas enregistrer ou télécharger des modifications.
*   **Cause** : Vous êtes en mode strict (`--strict`) et votre `STATE.json` ne correspond pas à l'état réel des fichiers.
*   **Solution** :
    1.  Exécutez `python tools/continuity_legacy/continuity_status.py` pour voir le tableau de bord de santé.
    2.  Synchronisez l'état à l'aide de `python tools/continuity_legacy/run_continuity_cycle.py`.
    3.  S'il s'agit d'une urgence, vous pouvez utiliser `git commit -m "msg" --no-verify` (non recommandé !).

---

## 3. Mon agent IA semble "perdu" ou ignore le contexte 🤖

*   **Problème** : L'IA commence à inventer des choses ou ne sait pas où la session précédente s'est arrêtée.
*   **Cause** : Vous n'avez pas remis le kit de démarrage canonique ou le `LIVE_HANDOFF.md` est vide/obsolète.
*   **Solution** :
    1.  Assurez-vous de remettre le fichier **`AGENT_START.md`** au début de la session.
    2.  Utilisez `python tools/continuity_legacy/continuity_suggest.py` pour générer un bon résumé de ce qui s'est passé et donnez-le à l'IA.
    3.  Demandez à l'IA : *"Reconstruct your current state by reading the root STATE.json and tell me what your Next Exact Action is"* (Reconstitue ton état actuel en lisant le STATE.json à la racine et dis-moi quelle est ta prochaine action exacte).

---

## 4. Erreur de "Security Warning" au démarrage ⚠️

*   **Problème** : Les scripts Python lancent une erreur de sécurité lors de la résolution du chemin racine.
*   **Cause** : Vous essayez d'exécuter les scripts en dehors d'un dépôt valide de **CONTINUITY LEGACY**.
*   **Solution** :
    1.  Assurez-vous d'être à la racine du projet.
    2.  Vérifiez que le fichier `continuity_legacy.json` ou le dossier `.continuity` existe.
    3.  Si vous avez copié le projet manuellement, assurez-vous d'exécuter d'abord `bootstrap_project.py`.

---

## 5. Le tableau de bord (`continuity_status`) affiche "Unknown" ou "Skipped" ❓

*   **Problème** : Une section du système de santé n'affiche pas de données.
*   **Cause** : Vous n'avez pas terminé un cycle complet de continuité ou la fonction "External Docs" est désactivée.
*   **Solution** :
    1.  Exécutez le cycle : `python tools/continuity_legacy/run_continuity_cycle.py`.
    2.  Si vous utilisez un dossier externe (ex: `MYPROJECTDEV`), assurez-vous d'avoir activé l'option lors du démarrage avec `--enable-external-docs`.

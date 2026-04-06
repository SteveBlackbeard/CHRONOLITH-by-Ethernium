# Continuity Legacy: Persistent Governance Layer 



`CONTINUITY LEGACY` est un kit de démarrage indépendant conçu pour construire des projets avec une continuité persistante, une mémoire canonique et un passage de relais (handoff) répétable entre les humains et les opérateurs d'IA.



Ce toolkit privilégie la continuité : il fournit une discipline réutilisable pour la persistance du contexte, la parité des documents et un transfert gouverné sans dépendre d'un framework externe.



## Ce que cela inclut

- une surface de mémoire canonique minimale

- un instantané de démarrage de continuité (snapshot)

- des vérifications de parité des documents

- des vérifications d'appartenance au système

- une couche optionnelle de développement externe (ex: `PROJECTDEV/`)

- une commande de clôture de continuité stricte

- un gestionnaire de démarrage (bootstrapper) pour personnaliser le modèle



## Démarrage Rapide



### 1. La Voie "Pro" (CLI) - RECOMMANDÉ

Installez l'interface de ligne de commande globale pour initialiser vos projets en une seule étape :



```powershell

pip install continuity-legacy

continuity-legacy init "Mon Projet"

```



### 2. Contrôle Manuel (Copier/Coller)

1. Copiez ce dossier à la racine de votre nouveau projet.

2. Lancez le gestionnaire de démarrage :



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Mon Projet" --project-slug mon_projet

```



3. Si vous souhaitez une couche de continuité externe :



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Mon Projet" --project-slug mon_projet --enable-external-docs

```



## Protection Automatique (Continuity Guard)

Pour garantir que le projet reste cohérent sans effort manuel, le kit inclut un système de sécurité à double couche :



1. **Garde Local (`pre-commit`)** : Installé par défaut. Utilise le mode "Soft" pour vous avertir des dérives ou des marqueurs manquants pendant que vous travaillez, sans bloquer votre flux créatif.

2. **Garde de Frontière (`pre-push`)** : Installé par défaut. Utilise le mode "Strict" pour **bloquer le push** vers GitHub si le cycle de continuité n'est pas valide à 100%.



## Fichiers Principaux

- `PROJECT_CONTEXT.md`

- `STATE.json`

- `ROADMAP.md`

- `.continuity/LIVE_HANDOFF.md`

- `AGENT_START.md` (Fichier à remettre à un nouvel agent IA)



---

**Pour plus de détails, consultez les cas d'utilisation et le guide de dépannage dans le répertoire racine.**

---

| Guide | Link |
| :--- | :--- |
| [**Industrial Guide**](../../../docs/HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../../docs/HOW_TO_USE_IT.md) |
| [**Release Manifest**](../../../RELEASE_NOTES_MANIFEST.md) | [RELEASE_NOTES_MANIFEST.md](../../../RELEASE_NOTES_MANIFEST.md) |

---

---
*Continuity Legacy: Protecting the logical lineage of your software.*

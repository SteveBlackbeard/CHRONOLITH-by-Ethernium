# Chronolith

![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)

Chronolith est une couche d'intégrité cryptographique pour les documents qui portent l'intention d'un projet à travers les sessions assistées par IA. Il transforme vos documents canoniques en arbre de Merkle, enregistre une référence signée et échoue en mode fermé dès que l'état courant ne lui correspond plus.

Il ne garantit pas qu'une IA « se souvienne ». Il fournit une trace vérifiable de ce que le contexte convenu *était*, et un arrêt net lorsqu'il dérive.

## Éditions

- **Lite** : transmission locale minimale et vérifications d'état signées.
- **Pro** : le gardien complet — références signées en Ed25519, chaîne de transparence en ajout seul, preuves d'inclusion Merkle, chiffrement, rotation de clés et ancrage Bitcoin.
- **Omega** : cartographie cognitive orientée RAG et analyse d'impact.

## Installation

```bash
pip install chronolith
chronolith --help
```

Paquets individuels :

```bash
pip install chronolith-lite
pip install chronolith-pro
pip install chronolith-omega
```

## Preuve vérifiable

Un état de ce projet est horodaté dans le **bloc Bitcoin 958484**. Vous n'avez pas à faire confiance à ce dépôt ni à son auteur — vérifiez-le vous-même :

```bash
pip install "chronolith-pro[anchor]"
chronolith-pro verify-anchor --proof docs/evidence/ANCHOR_3647dd737ee8.json.ots
```

Ce que cela prouve : ces données exactes existaient avant que ce bloc ne soit miné. Ce que cela ne prouve pas : qui les a écrites, ni qu'elles sont correctes. Ces limites sont documentées, pas dissimulées.

## Périmètre du produit

Chronolith est le runtime Python et le noyau de gouvernance. Seneschal est un outil distinct et extractible pour la frugalité en jetons et les octrois de capacités signés.

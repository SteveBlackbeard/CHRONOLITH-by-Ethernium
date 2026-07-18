# Chronolith

![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)

Chronolith è uno strato di integrità crittografica per i documenti che trasportano l'intento di un progetto attraverso le sessioni assistite dall'IA. Trasforma i documenti canonici in un albero di Merkle, registra una linea di base firmata e fallisce in modo fail-closed quando lo stato attuale non vi corrisponde più.

Non garantisce che un'IA «ricordi». Fornisce una traccia verificabile di ciò che il contesto concordato *era*, e un arresto netto quando devia.

## Edizioni

- **Lite**: passaggio di consegne locale minimo e controlli di stato firmati.
- **Pro**: il guardiano completo — linee di base firmate con Ed25519, catena di trasparenza in sola aggiunta, prove di inclusione Merkle, cifratura, rotazione delle chiavi e ancoraggio su Bitcoin.
- **Omega**: mappatura cognitiva orientata al RAG e analisi d'impatto.

## Installazione

```bash
pip install chronolith
chronolith --help
```

Pacchetti singoli:

```bash
pip install chronolith-lite
pip install chronolith-pro
pip install chronolith-omega
```

## Prova verificabile

Uno stato di questo progetto è marcato temporalmente nel **blocco Bitcoin 958484**. Non devi fidarti di questo repository né del suo autore: verificalo tu stesso:

```bash
pip install "chronolith-pro[anchor]"
chronolith-pro verify-anchor --proof docs/evidence/ANCHOR_3647dd737ee8.json.ots
```

Cosa dimostra: che quei dati esatti esistevano prima che quel blocco fosse minato. Cosa non dimostra: chi li ha scritti, né che siano corretti. Questi limiti sono documentati, non nascosti.

## Confine del prodotto

Chronolith è il runtime Python e il nucleo di governance. Seneschal è uno strumento separato ed estraibile per la frugalità dei token e le concessioni di capacità firmate.

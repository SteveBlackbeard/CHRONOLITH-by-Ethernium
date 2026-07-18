# Chronolith

![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)

Chronolith é uma camada de integridade criptográfica para os documentos que transportam a intenção de um projeto ao longo de sessões assistidas por IA. Converte os teus documentos canónicos numa árvore de Merkle, regista uma linha de base assinada e falha em modo fechado quando o estado atual deixa de corresponder.

Não garante que uma IA «se lembre». Dá-te um registo verificável do que o contexto acordado *era*, e uma paragem imediata quando este deriva.

## Edições

- **Lite**: transferência local mínima e verificações de estado assinadas.
- **Pro**: o guardião completo — linhas de base assinadas com Ed25519, cadeia de transparência apenas de adição, provas de inclusão Merkle, cifragem, rotação de chaves e ancoragem em Bitcoin.
- **Omega**: mapeamento cognitivo orientado a RAG e análise de impacto.

## Instalação

```bash
pip install chronolith
chronolith --help
```

Pacotes individuais:

```bash
pip install chronolith-lite
pip install chronolith-pro
pip install chronolith-omega
```

## Prova verificável

Um estado deste projeto está datado no **bloco Bitcoin 958484**. Não tens de confiar neste repositório nem no seu autor — verifica-o tu mesmo:

```bash
pip install "chronolith-pro[anchor]"
chronolith-pro verify-anchor --proof docs/evidence/ANCHOR_3647dd737ee8.json.ots
```

O que prova: que esses dados exatos existiam antes de esse bloco ser minerado. O que não prova: quem os escreveu, nem que estejam corretos. Esses limites estão documentados, não escondidos.

## Fronteira do produto

Chronolith é o runtime Python e o núcleo de governação. Seneschal é uma ferramenta separada e extraível para frugalidade de tokens e concessões de capacidade assinadas.

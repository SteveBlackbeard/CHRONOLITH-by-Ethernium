# Contributing to Ethernium Continuity Legacy 🏛️🧠🦾

Welcome to the **Ethernium Forge**. We are building the foundational infrastructure for the long-term cognitive continuity of software. Your contributions are vital to protecting the logical lineage of our world.

## 🏛️ Code of Honor
Ethernium is a place of precision, high-fidelity, and technical excellence. We value:
- **Clarity**: Documentation belongs next to the code.
- **Parity**: A change in one edition (Lite) must be synchronized or accounted for in the others (Pro, Omega).
- **Symmetry**: Emojis are tactical nucleotides; they must be visually consistent across all localized versions.

## 🛰️ Workflow: The DNA Cycle
1.  **Fork** the repository and create your feature branch.
2.  **Logic First**: Ensure your code passes the existing `pytest` suite.
3.  **DNA Synthesis**: Run `python sync_translations.py --auto-gen` to propagate your changes across the 9 localized `README` and `RELEASE` files.
4.  **Crystallization**: Verify that your changes do not break the Merkle Root validation.
5.  **Submission**: Open a Pull Request with a clear description of the "Intent Capture" (The *Why*).

## 🛠️ Setup the Forge
```bash
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/CONTINUITY-LEGACY-by-Ethernium.git
cd CONTINUITY-LEGACY-by-Ethernium

# 2. Setup environment
pip install -e continuity-lite
pip install -r requirements-dev.txt

# 3. Active Guardian
python setup_guardian.py
```

## 🔍 Technical Paradoxes
If you are modifying the **Merkle Tree** or the **DNA Synthesis** logic, you must provide unit tests in `tests/` that prove no drift occurs across Windows and Unix environments.

---
*Ethernium Sentinels - Forging the future of cognitive software.* 🏛️💎🦾

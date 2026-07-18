# Contributing to CHRONOLITH



First of all, thank you for considering contributing! This project is built on the philosophy of persistent chronolith, and we welcome improvements that align with that vision.



## How Can I Contribute?



### Reporting Bugs

If you find a technical bug or a chronolith break:

1.  Search the [issues](https://github.com/SteveBlackbeard/CHRONOLITH-by-Ethernium/issues) to see if it's already reported.

2.  If not, open a new issue with a clear title and description.

3.  Include steps to reproduce, what you expected, and what actually happened.



### Suggesting Improvements

We are always looking for better ways to:

-   Improve document parity validation.

-   Refine the boot sequence logic.

-   Enhance the CLI automation.



### Submitting a Pull Request

1.  Fork the repository.

2.  Create a new branch for your feature or fix (e.g., `git checkout -b feat/my-new-feature`).

3.  Make your changes.

4.  **Run the Chronolith Cycle!** (See `tools/chronolith/run_chronolith_cycle.py`).

5.  **Chronolith Proof**: Your PR must include a `outputs/chronolith/chronolith_cycle_report.json` showing a `status: ok` as proof of alignment.

6.  Commit your changes with a clear message.

7.  Push to your fork and open a Pull Request to the `Ethernium` branch.



## 🏛️ Governance

This project follows a merit-based governance model. Total project alignment is tracked via the chronolith system itself. See [MAINTAINERS.md](file:///d:/Experimentos/CHRONOLITH_LEGACY/MAINTAINERS.md) for more information on roles and leadership.



## ⚖️ Flexible Validation (v2.2)

We support different severity levels for documentation parity:

- **Error**: Mandatory. Blocks commit/push.

- **Warning**: Recommended. Notified but non-blocking locally.

- **Info**: Informative feedback.



For critical exceptions, use the `BYPASS_LOG.md` to document why a rule was temporarily waived.



## 🎨 Code Style

-   Use Python 3.8+ compatible code.

-   Be strict with `utf-8` encoding.

-   Always prioritize readability and chronolith over clever shortcuts.

-   Follow the existing path resolution and security patterns.



---

**Thank you for helping us build better, persistent chronolith!**

---
*Chronolith: Protecting the logical lineage of your software.*

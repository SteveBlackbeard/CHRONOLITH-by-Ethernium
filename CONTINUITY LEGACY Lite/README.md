# CONTINUITY LEGACY Lite ⚡🌱
**The Zero-Overhead AI Continuity Engine.**

This is a stripped-down, high-speed implementation of the CONTINUITY LEGACY framework, designed for personal projects, rapid prototyping, and solo AI-pair-programming.

## 🚀 Quick Start

1.  **Initialize**: Create three files in your root:
    - `PROJECT_CONTEXT.md`: The rules and stack of your project.
    - `STATE.json`: The current status and next steps.
    - `LIVE_HANDOFF.md`: The exact next action for the AI.

2.  **Run Sync**: 
    ```bash
    python run_continuity_lite.py
    ```
    This updates your `STATE.json` with Git metadata and validates that your core documents exist.

## 🧠 Why Lite?
- **Zero Dependencies**: Pure Python 3. Standard library only.
- **Git Native**: Auto-detects branch and commit hashes if git is available.
- **Low Ceremony**: No heavy folders or dashboards. Just three files and one script.

## 🛠️ Evolution
When your project grows, you can migrate to **[CONTINUITY LEGACY Pro](../CONTINUITY%20LEGACY%20Pro)**.

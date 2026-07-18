# CHRONOLITH: Troubleshooting Guide 🛠️



Something doesn't match? Don't panic. Here are the solutions to common chronolith issues.



---



## 1. Parity Cycle Fails (`doc_parity_check`) ✘



*   **Problem**: You receive a "Document parity drift" error indicating missing mandatory markers.

*   **Cause**: You edited a file (e.g. README or Handoff) and accidentally deleted a line that the system monitors to ensure consistency.

*   **Solution**:

    1.  Check the report in `outputs/chronolith/chronolith_cycle_report.json` to see which "required_string" is missing.

    2.  Add the parity marker back into the document.

    3.  Run `python tools/chronolith/run_chronolith_cycle.py` again.



---



## 2. Git Hook Blocks My Commit/Push 🛡️



*   **Problem**: Git won't let you save or upload changes.

*   **Cause**: You are in strict mode (`--strict`) and your `STATE.json` does not match the actual state of the files.

*   **Solution**:

    1.  Run `python tools/chronolith/chronolith_status.py` to see the Health Dashboard.

    2.  Sync the state using `python tools/chronolith/run_chronolith_cycle.py`.

    3.  If it's an emergency, you can use `git commit -m "msg" --no-verify` (Not recommended!).



---



## 3. My AI Agent Seems "Lost" or Ignores Context 🤖



*   **Problem**: The AI starts making things up or doesn't know where the previous session left off.

*   **Cause**: You haven't handed over the canonical starter pack or `LIVE_HANDOFF.md` is empty/outdated.

*   **Solution**:

    1.  Ensure you hand over the **`AGENT_START.md`** file at the beginning of the session.

    2.  Use `python tools/chronolith/chronolith_suggest.py` to generate a good summary of what has happened and give it to the AI.

    3.  Ask the AI: *"Reconstruct your current state by reading the root STATE.json and tell me what your Next Exact Action is"*.



---



## 4. "Security Warning" Error on Startup ⚠️



*   **Problem**: Python scripts throw a security error when trying to resolve the root path.

*   **Cause**: You are trying to run the scripts outside of a valid **CHRONOLITH** repository.

*   **Solution**:

    1.  Ensure you are in the project root.

    2.  Check that the `chronolith.json` file or `.chronolith` folder exists.

    3.  If you copied the project manually, ensure you run `bootstrap_project.py` first.



---



## 5. Dashboard (`chronolith_status`) Shows "Unknown" or "Skipped" ❓



*   **Problem**: Some section of the health system shows no data.

*   **Cause**: You haven't completed a full chronolith cycle or the "External Docs" feature is disabled.

*   **Solution**:

    1.  Run the cycle: `python tools/chronolith/run_chronolith_cycle.py`.

    2.  If using an external folder (e.g. `MYPROJECTDEV`), ensure you enabled it in the bootstrap with `--enable-external-docs`.

---
*Chronolith: Protecting the logical lineage of your software.*

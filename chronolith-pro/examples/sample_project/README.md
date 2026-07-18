# Chronolith: Persistent Governance Layer 



This directory demonstrates how CHRONOLITH maintains project state across development sessions.



## How to use this example:

1. Copy this sample_project folder to a new location.

2. Run the chronolith cycle:

   python ../../tools/chronolith/run_chronolith_cycle.py --repo-root .

3. Observe how it validates the existing logs.

4. Try deleting DECISIONS_LOG.md and see it flag the project as 'attention_required'.



## Before and After:

- **Before**: Fragmented commits with no clear strategic context.

- **After**: A canonical STATE.json and DECISIONS_LOG.md that allow any AI or developer to resume work instantly.



| Guide | Link |
| :--- | :--- |
| [**Industrial Guide**](../../../HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../../HOW_TO_USE_IT.md) |
| [**Release Manifest**](../../../RELEASE_NOTES_MANIFEST.md) | [RELEASE_NOTES_MANIFEST.md](../../../RELEASE_NOTES_MANIFEST.md) |

---

---
*Chronolith: Protecting the logical lineage of your software.*

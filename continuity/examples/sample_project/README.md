# Sample Project: Continuity Legacy in Action

This directory demonstrates how CONTINUITY LEGACY maintains project state across development sessions.

## How to use this example:
1. Copy this sample_project folder to a new location.
2. Run the continuity cycle:
   python ../../tools/continuity_legacy/run_continuity_cycle.py --repo-root .
3. Observe how it validates the existing logs.
4. Try deleting DECISIONS_LOG.md and see it flag the project as 'attention_required'.

## Before and After:
- **Before**: Fragmented commits with no clear strategic context.
- **After**: A canonical STATE.json and DECISIONS_LOG.md that allow any AI or developer to resume work instantly.

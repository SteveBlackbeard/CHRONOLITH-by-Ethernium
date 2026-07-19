# Change Contract: Refresh The Golden Baseline After The Chronolith Rename

## Summary

Regenerate `.chronolith/golden-baseline.json`. It has recorded pre-rename
hashes since `7b5a2ac`, so `golden_baseline.py verify` has failed on every CI
run from that commit onward and the Industrial Guardian job has been red the
whole time.

## Scope

Files expected to change:

- `.chronolith/golden-baseline.json`

Out of scope:

- every file the baseline covers. Not one of them is edited by this contract.
  The baseline is wrong; the tree is not.

## Reason

The rename changed governed content and did not regenerate the baseline in the
same commit. The evidence that this is a stale baseline rather than drift is in
the byte counts: `feature-registry.json` (2395), `rulebook.json` (3294),
`PROJECT_DNA.md` (6123) and `VERSION` (6) each hash differently at *identical
size* — the signature of a same-length substitution, `CONTINUITY` for
`CHRONOLITH`, ten characters for ten.

Three further files differ because they were legitimately edited afterwards:
`README.md` gained the Omega section and the GETTING_STARTED link,
`industrial_guardian.yml` and `pyproject.toml` changed with the release work.
Those edits are already reviewed and committed.

A guard that has cried wolf since July is worse than no guard: nobody reads a
list that is permanently red, so a real drift would now pass unnoticed.

## Risk

Risk level: `low`

The baseline is a record of expected hashes. Refreshing cannot change runtime
behavior. The genuine risk is the opposite of a regression — that a refresh
silently blesses an unintended change — which is why the scope above is
explicit and each difference is accounted for.

Potential failure modes:

- **encoding drift**: the refresh command hashes files as they sit on disk. On
  Windows the working tree carries CRLF while the committed blobs are LF, so a
  refresh run from Windows would encode CRLF hashes and fail on Linux CI,
  trading one red build for another. The working tree is normalized to LF
  before refreshing, and the result is verified against `git cat-file` output
  rather than against local files.

## Verification

Required checks:

```text
python scripts/golden_baseline.py verify
python scripts/audit_all.py
```

Every baseline entry is additionally compared against the content of the
corresponding git blob, which is what CI checks out.

## Rollback

```text
git checkout HEAD~1 -- .chronolith/golden-baseline.json
```

The baseline is a single generated file with no dependents; reverting it
restores the previous expectations exactly.

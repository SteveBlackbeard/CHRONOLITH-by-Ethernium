from pathlib import Path

hook = (
    "#!/bin/sh\n"
    "# Chronolith Sentinel Guardian (v2.4.2 - Fail-Closed)\n"
    "echo '[*] Ethernium: Guarding DNA Lineage...'\n"
    "python .github/scripts/crystalize.py\n"
    "RESULT=$?\n"
    "if [ $RESULT -ne 0 ]; then\n"
    "  echo '[!] PUSH REJECTED: DNA Synthesis failed.'\n"
    "  exit 1\n"
    "fi\n"
    "echo '[+] DNA Parity Confirmed. Push authorized.'\n"
    "exit 0\n"
)

# CRITICAL: write_bytes to force LF-only (no CRLF)
Path(".git/hooks/pre-push").write_bytes(hook.encode("utf-8"))
print("[+] pre-push hook written with LF-only line endings.")

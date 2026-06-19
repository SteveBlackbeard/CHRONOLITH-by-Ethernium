"""Lightweight defensive prompt-risk classifier."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all previous",
    "disregard previous instructions",
    "override the system",
    "system prompt",
    "developer message",
    "reveal your instructions",
    "do not tell the user",
    "run this command",
    "exfiltrate",
    "tool call",
    "send the contents",
)

ZERO_WIDTH = ("\u200b", "\u200c", "\u200d", "\ufeff")


@dataclass(frozen=True)
class PromptRisk:
    source: str
    trust: str
    score: int
    findings: tuple[str, ...]

    @property
    def blocked(self) -> bool:
        return self.score >= 3

    @property
    def severity(self) -> str:
        if self.blocked:
            return "block"
        if self.score:
            return "warning"
        return "info"


def classify_text(text: str, *, source: str = "external") -> PromptRisk:
    lowered = text.lower()
    findings: list[str] = []
    for marker in INJECTION_MARKERS:
        if marker in lowered:
            findings.append(f"injection marker: {marker}")
    if any(char in text for char in ZERO_WIDTH):
        findings.append("hidden unicode marker")
    if "api_key" in lowered or "secret_key" in lowered or "-----begin private key-----" in lowered:
        findings.append("possible secret material")
    if "http://" in lowered or "https://" in lowered:
        findings.append("external link present")

    trust = "low" if source in {"external", "web", "pdf", "ocr", "generated"} else "medium"
    score = len(findings)
    if trust == "low" and findings:
        score += 1
    if trust == "low" and any(finding.startswith("injection marker:") for finding in findings):
        score += 1
    return PromptRisk(source=source, trust=trust, score=score, findings=tuple(findings))


def classify_file(path: Path, *, source: str = "external") -> PromptRisk:
    text = path.read_text(encoding="utf-8", errors="replace")
    return classify_text(text, source=source)

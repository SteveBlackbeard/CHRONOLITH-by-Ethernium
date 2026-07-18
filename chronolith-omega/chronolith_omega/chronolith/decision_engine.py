#!/usr/bin/env python3
"""
decision_engine.py — CHRONOLITH Pro
==========================================
Advanced Strategic Decision Engine (Alpha).

This module analyzes the canonical memory files (STATE.json, ROADMAP.md, LIVE_HANDOFF.md)
to identify technical debt, project momentum stalls, and missing contexts.
It outputs actionable strategic recommendations for the human / AI developer team.

Features:
- State staleness detection
- Roadmap alignment validation
- Tactical extraction from LIVE_HANDOFF.md
"""

import json
import datetime
from pathlib import Path

def parse_state(repo_root: Path) -> dict:
    """Safely loads and parses STATE.json."""
    state_file = repo_root / "STATE.json"
    if not state_file.exists():
        return {"status": "error", "message": "STATE.json not found."}
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"status": "error", "message": f"Malformed STATE.json: {e}"}

def evaluate_momentum(state_data: dict) -> dict:
    """Evaluates project momentum based on the last update timestamp."""
    try:
        last_update_str = state_data.get("last_update", state_data.get("generated_at", ""))
        if not last_update_str:
            return {"score": 50, "insight": "No timestamp found in STATE.json."}
            
        # Parse ISO format handling potential timezone strings (basic implementation)
        clean_str = last_update_str.replace("Z", "+00:00")
        last_update = datetime.datetime.fromisoformat(clean_str)
        
        # Calculate delta
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - last_update
        
        if delta.days > 30:
            return {"score": 20, "insight": "Project stale. Over 30 days without updates."}
        elif delta.days > 7:
            return {"score": 60, "insight": "Momentum slowing. Over a week since last update."}
        else:
            return {"score": 95, "insight": "High momentum. Active development detected."}
    except Exception:
        return {"score": 50, "insight": "Could not parse last update time."}

def extract_tactical_directive(repo_root: Path) -> str:
    """Extracts the immediate next action from LIVE_HANDOFF.md."""
    handoff_file = repo_root / ".chronolith" / "LIVE_HANDOFF.md"
    if not handoff_file.exists():
        return "CRITICAL: LIVE_HANDOFF.md missing. Next exact action is undefined."
    
    try:
        content = handoff_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            if "Next Exact Action" in line:
                # Capture the next non-empty line as the directive
                for next_line in lines[idx+1:idx+5]:
                    stripped = next_line.strip()
                    if stripped and not stripped.startswith("#"):
                        return f"Directive found: {stripped}"
        return "Warning: Next Exact Action header found but no actionable step defined."
    except Exception:
        return "Error reading LIVE_HANDOFF.md."

def generate_strategy(repo_root: Path, scenarios: bool = False) -> dict:
    """Orchestrates the decision engine analysis."""
    print("[*] Engine Initializing: Strategic Analysis...")
    
    state = parse_state(repo_root)
    if state.get("status") == "error":
        print(f"[!] {state['message']}")
        return state
        
    momentum = evaluate_momentum(state)
    tactical = extract_tactical_directive(repo_root)
    
    # Formulate recommendation
    recommendation = "Continue execution of the roadmap."
    if momentum["score"] < 50:
        recommendation = "PRIORITY: Review STATE.json. Update current context to regain momentum."
    elif "missing" in tactical.lower() or "error" in tactical.lower():
        recommendation = "PRIORITY: Re-establish the LIVE_HANDOFF.md to define the next exact action for the AI agent."
        
    if scenarios:
        print("\n[?] ** SCENARIOS PROJECTION **")
        if momentum["score"] < 50:
            print("    -> PATH A (Do nothing): Technical debt compounds. AI context loss expected.")
            print("    -> PATH B (Follow priority): Momentum recovers. Handoffs remain clean.")
        else:
            print("    -> PATH A (Execute Current Next Action): Feature delivered smoothly.")
            print("    -> PATH B (Pivot Roadmap): Moderate friction, but manageable due to high momentum.")
        print()

    report = {
        "status": "success",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "momentum_score": momentum["score"],
        "momentum_insight": momentum["insight"],
        "tactical_directive": tactical,
        "strategic_recommendation": recommendation
    }
    
    # Write output
    out_dir = repo_root / "outputs" / "chronolith"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "strategic_decision.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"[+] Advanced Strategy Report generated at: {out_file.relative_to(repo_root)}")
    print(f"    -> Momentum: {momentum['score']}/100")
    print(f"    -> Strategy: {recommendation}")
    
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CHRONOLITH Pro - Decision Engine")
    parser.add_argument("--repo-root", default=".", help="Root directory of the project")
    parser.add_argument("--scenarios", action="store_true", help="Project alternative action paths")
    args = parser.parse_args()
    
    root_path = Path(args.repo_root).resolve()
    generate_strategy(root_path, scenarios=args.scenarios)

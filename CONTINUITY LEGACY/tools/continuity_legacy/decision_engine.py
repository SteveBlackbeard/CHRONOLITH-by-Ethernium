#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add core to sys.path for relative imports if needed
sys.path.append(str(Path(__file__).parent.parent))

from continuity_legacy.core.automation_common import (
    load_config,
    read_text,
    state_path,
    context_path,
    resolve_repo_root,
    Color,
    echo
)

def analyze_strategy(repo_root: Path):
    """
    Analyzes the 'Truth' (PROJECT_CONTEXT) vs 'Reality' (STATE.json)
    to propose a strategic decision.
    """
    config = load_config(repo_root)
    state_file = state_path(repo_root, config)
    context_file = context_path(repo_root, config)
    
    if not state_file.exists() or not context_file.exists():
        return "ERROR: Context/State missing."

    state = json.loads(state_file.read_text(encoding="utf-8"))
    context = context_file.read_text(encoding="utf-8")
    
    current_status = state.get("status", "unknown")
    next_actions = state.get("next_actions", [])
    
    echo(f"[*] Analyzing Strategy for {config.get('project_name')}...", Color.CYAN)
    
    # Simple logic-based decision engine (Prototype)
    # Future versions will use vector search/LLM reasoning
    
    decision = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "proposed_action": "",
        "rationale": "",
        "risk_level": "low"
    }

    if not next_actions:
        decision["proposed_action"] = "Initialize Project Roadmap"
        decision["rationale"] = "No next actions defined in STATE.json."
    elif current_status == "setup":
        decision["proposed_action"] = "Standardize Core Modules"
        decision["rationale"] = "Project is in early setup phase; focus on architectural stability."
    else:
        # Placeholder for more complex logic
        decision["proposed_action"] = f"Scale {current_status} to next milestone: {next_actions[0]}"
        decision["rationale"] = "Continuing established roadmap momentum."

    return decision

def run_engine():
    root = resolve_repo_root(None, __file__)
    decision = analyze_strategy(root)
    
    output_path = root / "outputs" / "continuity" / "strategic_decision.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(decision, f, indent=2)
        
    echo(f"[✔] Strategic Decision Generated: {decision['proposed_action']}", Color.GREEN)
    echo(f"[!] Rationale: {decision['rationale']}", Color.WHITE)

if __name__ == "__main__":
    run_engine()

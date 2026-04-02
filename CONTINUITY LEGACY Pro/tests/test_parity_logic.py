import pytest
from pathlib import Path
import json
import os
import sys

# Add tools to path
sys.path.append(str(Path(__file__).parent.parent / 'tools' / 'continuity_legacy'))

from doc_parity_check import run_parity_check

def test_parity_check_functional(tmp_path):
    # Setup a mock project root
    repo_root = tmp_path
    cont_dir = repo_root / '.continuity'
    cont_dir.mkdir()
    
    # Create required files
    (cont_dir / 'DECISIONS_LOG.md').write_text("# Decisions", encoding='utf-8')
    (cont_dir / 'CONTEXT_CONTINUITY.md').write_text("# Context", encoding='utf-8')
    (cont_dir / 'TIMELINE.md').write_text("# Timeline", encoding='utf-8')
    (repo_root / 'README.md').write_text("# README", encoding='utf-8')
    (repo_root / 'STATE.json').write_text(json.dumps({"phase": "test"}), encoding='utf-8')
    (repo_root / 'continuity_legacy.json').write_text(json.dumps({
        "project_name": "Test",
        "tool_version": "5.0.0"
    }), encoding='utf-8')
    
    # Run check
    report = run_parity_check(None, str(repo_root))
    
    # Assert
    assert report['status'] == 'ok'
    assert 'Diferencia de paridad (checksum)' not in str(report)

def test_parity_fails_on_missing_file(tmp_path):
    repo_root = tmp_path
    (repo_root / '.continuity').mkdir()
    (repo_root / 'README.md').write_text("# README", encoding='utf-8')
    
    report = run_parity_check(None, str(repo_root))
    assert report['status'] != 'ok'
    assert 'attention_required' in report['status']


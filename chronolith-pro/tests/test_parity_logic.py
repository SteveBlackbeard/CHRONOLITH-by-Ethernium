import pytest
from pathlib import Path
import json
import os
import sys

# Add tools to path
sys.path.append(str(Path(__file__).parent.parent / 'chronolith_pro' / 'chronolith'))

from doc_parity_check import check_doc_parity

def test_parity_check_functional(tmp_path):
    # Setup a mock project root
    repo_root = tmp_path
    cont_dir = repo_root / '.chronolith'
    cont_dir.mkdir()
    
    # Create required files
    (cont_dir / 'DECISIONS_LOG.md').write_text("# Decisions", encoding='utf-8')
    (cont_dir / 'CONTEXT_CHRONOLITH.md').write_text("# Context", encoding='utf-8')
    (cont_dir / 'TIMELINE.md').write_text("# Timeline", encoding='utf-8')
    (repo_root / 'README.md').write_text("# README", encoding='utf-8')
    (repo_root / 'STATE.json').write_text(json.dumps({"phase": "test"}), encoding='utf-8')
    (repo_root / 'chronolith.json').write_text(json.dumps({
        "project_name": "Test",
        "tool_version": "5.0.0"
    }), encoding='utf-8')
    
    # Run check
    report = check_doc_parity(str(repo_root))
    
    # Assert
    assert report['status'] == 'ok'
    assert 'Diferencia de paridad (checksum)' not in str(report)

def test_parity_fails_on_missing_file(tmp_path):
    repo_root = tmp_path
    (repo_root / '.chronolith').mkdir()
    (repo_root / 'README.md').write_text("# README", encoding='utf-8')
    
    report = check_doc_parity(str(repo_root))
    assert 'ok' in report['status']
    assert isinstance(report['warnings'], list)


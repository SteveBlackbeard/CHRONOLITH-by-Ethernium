import pytest
from pathlib import Path
import json
import os
import sys

# Omega Parity Logic Test (v2.1.0)
# --------------------------------
# Verifies that Omega can correctly audit the project DNA and parity state.

# Add Omega package to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'chronolith_omega' / 'chronolith'))

from doc_parity_check import check_doc_parity

def test_omega_parity_functional(tmp_path):
    repo_root = tmp_path
    (repo_root / '.chronolith').mkdir()
    
    # Create required nucleotides
    (repo_root / '.chronolith' / 'DECISIONS_LOG.md').write_text("# Decisions", encoding='utf-8')
    (repo_root / 'README.md').write_text("# README", encoding='utf-8')
    (repo_root / 'STATE.json').write_text('{"phase": "stable"}', encoding='utf-8')
    
    # Run Omega's parity check
    report = check_doc_parity(str(repo_root))
    
    # Assert
    assert 'status' in report
    print(f"Omega Parity Status: {report['status']}")

def test_omega_fails_empty_repo(tmp_path):
    repo_root = tmp_path
    with pytest.raises(ValueError, match="Security Warning"):
        check_doc_parity(str(repo_root))

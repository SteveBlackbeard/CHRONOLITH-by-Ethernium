import pytest
from pathlib import Path
import os
import sys

# Continuity Lite DNA Test (v2.1.0)
# ----------------------------------
# Verifies that Lite correctly generates the PROJECT_DNA.md artifact.

# Add Lite package to path
sys.path.append(str(Path(__file__).parent.parent / 'continuity_lite' / 'continuity_legacy'))

from run_continuity_lite import generate_minimal_dna

def test_lite_dna_synthesis(tmp_path):
    repo_root = tmp_path
    
    # Create mock nucleotides
    (repo_root / 'README.md').write_text("# Test README", encoding='utf-8')
    (repo_root / 'NOTES.md').write_text("# Test Notes", encoding='utf-8')
    
    # Run DNA Synthesis
    generate_minimal_dna(repo_root)
    
    # DNA path
    dna_path = repo_root / 'PROJECT_DNA.md'
    
    # Assert
    assert dna_path.exists()
    content = dna_path.read_text(encoding='utf-8')
    assert 'README.md' in content
    assert 'NOTES.md' in content
    assert 'DNA Manifest' in content

def test_lite_dna_skips_git(tmp_path):
    repo_root = tmp_path
    (repo_root / '.git').mkdir()
    (repo_root / '.git' / 'config').write_text('config content', encoding='utf-8')
    (repo_root / 'README.md').write_text("# README", encoding='utf-8')
    
    generate_minimal_dna(repo_root)
    
    dna_path = repo_root / 'PROJECT_DNA.md'
    content = dna_path.read_text(encoding='utf-8')
    assert 'config' not in content
    assert 'README.md' in content

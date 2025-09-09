"""
Pytest configuration and fixtures for BitWipers tests.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Common test fixtures
import pytest


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.bin"
    file_path.write_bytes(b"Test data" * 100)
    return str(file_path)


@pytest.fixture
def mock_device():
    """Mock device information for testing."""
    return {
        'name': 'Test Device',
        'path': '/dev/test',
        'size': 1024 * 1024 * 100,  # 100 MB
        'type': 'hdd',
        'interface': 'SATA',
        'serial': 'TEST123',
        'partitions': 1
    }

"""
Tests for data wiper functionality.
"""

import pytest
import os
import tempfile
from datetime import datetime
from bitwipers.core.wiper import DataWiper, WipeStatus, WipeResult
from bitwipers.core.patterns import WipePattern


class TestWipeResult:
    """Test suite for WipeResult dataclass."""
    
    def test_wipe_result_initialization(self):
        """Test WipeResult initialization."""
        result = WipeResult(
            device_path="/tmp/test",
            pattern=WipePattern.NIST_CLEAR,
            status=WipeStatus.PENDING,
            start_time=datetime.now()
        )
        assert result.device_path == "/tmp/test"
        assert result.pattern == WipePattern.NIST_CLEAR
        assert result.status == WipeStatus.PENDING
        assert result.bytes_wiped == 0
        assert result.total_bytes == 0
    
    def test_wipe_result_progress(self):
        """Test progress calculation."""
        result = WipeResult(
            device_path="/tmp/test",
            pattern=WipePattern.NIST_CLEAR,
            status=WipeStatus.IN_PROGRESS,
            start_time=datetime.now(),
            total_bytes=1000,
            bytes_wiped=500
        )
        assert result.progress_percent == 50.0
    
    def test_wipe_result_duration(self):
        """Test duration calculation."""
        start = datetime.now()
        result = WipeResult(
            device_path="/tmp/test",
            pattern=WipePattern.NIST_CLEAR,
            status=WipeStatus.COMPLETED,
            start_time=start,
            end_time=datetime.now()
        )
        assert result.duration >= 0


class TestDataWiper:
    """Test suite for DataWiper class."""
    
    def test_data_wiper_initialization(self):
        """Test DataWiper initialization."""
        wiper = DataWiper(block_size=4096, verify_wipe=True)
        assert wiper.block_size == 4096
        assert wiper.verify_wipe == True
        assert wiper._cancelled == False
    
    def test_wipe_file_nonexistent(self):
        """Test wiping a non-existent file."""
        wiper = DataWiper()
        result = wiper.wipe_file("/nonexistent/file.txt")
        assert result.status == WipeStatus.FAILED
        assert "not found" in result.error_message.lower()
    
    def test_wipe_file_small(self):
        """Test wiping a small temporary file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            temp_path = f.name
            f.write(b"Test data to be wiped" * 100)
        
        try:
            # Wipe the file
            wiper = DataWiper(verify_wipe=False)
            result = wiper.wipe_file(temp_path, pattern=WipePattern.ZERO_FILL, remove_file=False)
            
            # Check result
            assert result.status == WipeStatus.COMPLETED
            assert result.bytes_wiped > 0
            
            # Verify file content is wiped (should be zeros)
            with open(temp_path, 'rb') as f:
                content = f.read(100)
                assert content == b'\x00' * 100
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_cancel_operation(self):
        """Test canceling a wipe operation."""
        wiper = DataWiper()
        wiper.cancel()
        assert wiper._cancelled == True

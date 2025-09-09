"""
Tests for data wiping patterns.
"""

import pytest
from bitwipers.core.patterns import WipePattern, WipePatterns


class TestWipePatterns:
    """Test suite for wipe patterns."""
    
    def test_pattern_enum_values(self):
        """Test that all pattern enum values are defined."""
        assert WipePattern.ZERO_FILL.value == "zero_fill"
        assert WipePattern.ONE_FILL.value == "one_fill"
        assert WipePattern.RANDOM.value == "random"
        assert WipePattern.NIST_CLEAR.value == "nist_clear"
        assert WipePattern.NIST_PURGE.value == "nist_purge"
    
    def test_get_pattern_description(self):
        """Test pattern description retrieval."""
        desc = WipePatterns.get_pattern_description(WipePattern.NIST_CLEAR)
        assert "NIST" in desc
        assert "Clear" in desc
    
    def test_zero_fill_pattern(self):
        """Test zero fill pattern generation."""
        pattern_gen = WipePatterns.get_pattern_data(WipePattern.ZERO_FILL, block_size=10)
        block = next(pattern_gen)
        assert len(block) == 10
        assert block == b'\x00' * 10
    
    def test_one_fill_pattern(self):
        """Test one fill pattern generation."""
        pattern_gen = WipePatterns.get_pattern_data(WipePattern.ONE_FILL, block_size=10)
        block = next(pattern_gen)
        assert len(block) == 10
        assert block == b'\xFF' * 10
    
    def test_random_pattern(self):
        """Test random pattern generation."""
        pattern_gen = WipePatterns.get_pattern_data(WipePattern.RANDOM, block_size=100)
        block1 = next(pattern_gen)
        block2 = next(pattern_gen)
        assert len(block1) == 100
        assert len(block2) == 100
        # Random blocks should be different
        assert block1 != block2
    
    def test_recommended_pattern_for_ssd(self):
        """Test recommended pattern selection for SSD."""
        pattern = WipePatterns.get_recommended_pattern('ssd')
        assert pattern == WipePattern.NIST_CLEAR
    
    def test_recommended_pattern_for_hdd(self):
        """Test recommended pattern selection for HDD."""
        pattern = WipePatterns.get_recommended_pattern('hdd')
        assert pattern == WipePattern.NIST_PURGE

"""
Data wiping patterns implementation following NIST SP 800-88 guidelines.
Provides secure erasure patterns for different storage media types.
"""

import os
import secrets
from enum import Enum
from typing import List, Iterator


class WipePattern(Enum):
    """Enumeration of supported wipe patterns."""
    
    # Single pass patterns
    ZERO_FILL = "zero_fill"           # All zeros (0x00)
    ONE_FILL = "one_fill"             # All ones (0xFF)
    RANDOM = "random"                 # Cryptographically secure random data
    
    # Multi-pass patterns
    DOD_3_PASS = "dod_3_pass"         # DoD 5220.22-M (3 passes)
    DOD_7_PASS = "dod_7_pass"         # DoD 5220.22-M (7 passes)
    GUTMANN = "gutmann"               # Gutmann 35-pass method
    
    # NIST recommended
    NIST_CLEAR = "nist_clear"         # NIST SP 800-88 Clear
    NIST_PURGE = "nist_purge"         # NIST SP 800-88 Purge


class WipePatterns:
    """Implementation of various data wiping patterns."""
    
    @staticmethod
    def get_pattern_data(pattern: WipePattern, block_size: int = 4096) -> Iterator[bytes]:
        """
        Generate pattern data for the specified wipe pattern.
        
        Args:
            pattern: The wipe pattern to use
            block_size: Size of data blocks to generate
            
        Yields:
            bytes: Pattern data blocks
        """
        if pattern == WipePattern.ZERO_FILL:
            yield from WipePatterns._zero_fill(block_size)
        elif pattern == WipePattern.ONE_FILL:
            yield from WipePatterns._one_fill(block_size)
        elif pattern == WipePattern.RANDOM:
            yield from WipePatterns._random_fill(block_size)
        elif pattern == WipePattern.DOD_3_PASS:
            yield from WipePatterns._dod_3_pass(block_size)
        elif pattern == WipePattern.DOD_7_PASS:
            yield from WipePatterns._dod_7_pass(block_size)
        elif pattern == WipePattern.NIST_CLEAR:
            yield from WipePatterns._nist_clear(block_size)
        elif pattern == WipePattern.NIST_PURGE:
            yield from WipePatterns._nist_purge(block_size)
        elif pattern == WipePattern.GUTMANN:
            yield from WipePatterns._gutmann_method(block_size)
        else:
            raise ValueError(f"Unsupported wipe pattern: {pattern}")
    
    @staticmethod
    def _zero_fill(block_size: int) -> Iterator[bytes]:
        """Generate zero-filled blocks."""
        zero_block = b'\x00' * block_size
        while True:
            yield zero_block
    
    @staticmethod
    def _one_fill(block_size: int) -> Iterator[bytes]:
        """Generate one-filled blocks."""
        one_block = b'\xFF' * block_size
        while True:
            yield one_block
    
    @staticmethod
    def _random_fill(block_size: int) -> Iterator[bytes]:
        """Generate cryptographically secure random blocks."""
        while True:
            yield secrets.token_bytes(block_size)
    
    @staticmethod
    def _dod_3_pass(block_size: int) -> Iterator[bytes]:
        """
        DoD 5220.22-M 3-pass method:
        Pass 1: All zeros (0x00)
        Pass 2: All ones (0xFF)  
        Pass 3: Random data
        """
        # Pass 1: Zeros
        yield from [b'\x00' * block_size]
        # Pass 2: Ones
        yield from [b'\xFF' * block_size]
        # Pass 3: Random
        yield from [secrets.token_bytes(block_size)]
    
    @staticmethod
    def _dod_7_pass(block_size: int) -> Iterator[bytes]:
        """
        DoD 5220.22-M 7-pass method:
        Extended version with pattern verification
        """
        patterns = [
            b'\x00',  # Pass 1: All zeros
            b'\xFF',  # Pass 2: All ones
            b'\x92',  # Pass 3: 10010010
            b'\x49',  # Pass 4: 01001001
            b'\x24',  # Pass 5: 00100100
            b'\x00',  # Pass 6: All zeros (verify)
            None      # Pass 7: Random
        ]
        
        for i, pattern in enumerate(patterns):
            if pattern is None:
                # Random pass
                yield secrets.token_bytes(block_size)
            else:
                yield pattern * block_size
    
    @staticmethod
    def _nist_clear(block_size: int) -> Iterator[bytes]:
        """
        NIST SP 800-88 Clear method:
        Single pass with zeros or random data
        """
        yield from WipePatterns._random_fill(block_size)
    
    @staticmethod
    def _nist_purge(block_size: int) -> Iterator[bytes]:
        """
        NIST SP 800-88 Purge method:
        Multiple passes with different patterns
        """
        # Pass 1: Random
        yield secrets.token_bytes(block_size)
        # Pass 2: Zeros
        yield b'\x00' * block_size
        # Pass 3: Random
        yield secrets.token_bytes(block_size)
    
    @staticmethod
    def _gutmann_method(block_size: int) -> Iterator[bytes]:
        """
        Gutmann 35-pass method for maximum security.
        Note: This is overkill for modern drives.
        """
        # Gutmann patterns (simplified for demonstration)
        gutmann_patterns = [
            b'\x55', b'\xAA', b'\x92', b'\x49', b'\x24', b'\x00', b'\x11',
            b'\x22', b'\x33', b'\x44', b'\x55', b'\x66', b'\x77', b'\x88',
            b'\x99', b'\xAA', b'\xBB', b'\xCC', b'\xDD', b'\xEE', b'\xFF',
            b'\x92', b'\x49', b'\x24', b'\x12', b'\xED', b'\xB8', b'\x74',
            b'\x36', b'\x1B', b'\x8D', b'\xC4', b'\x62', b'\x31', b'\x18'
        ]
        
        for pattern in gutmann_patterns:
            if len(pattern) == 1:
                yield pattern * block_size
            else:
                # For multi-byte patterns, repeat to fill block
                full_pattern = (pattern * ((block_size // len(pattern)) + 1))[:block_size]
                yield full_pattern
    
    @staticmethod
    def get_pattern_description(pattern: WipePattern) -> str:
        """Get human-readable description of wipe pattern."""
        descriptions = {
            WipePattern.ZERO_FILL: "Single pass with zeros (0x00)",
            WipePattern.ONE_FILL: "Single pass with ones (0xFF)",
            WipePattern.RANDOM: "Single pass with random data",
            WipePattern.DOD_3_PASS: "DoD 5220.22-M 3-pass method",
            WipePattern.DOD_7_PASS: "DoD 5220.22-M 7-pass method",
            WipePattern.NIST_CLEAR: "NIST SP 800-88 Clear method",
            WipePattern.NIST_PURGE: "NIST SP 800-88 Purge method",
            WipePattern.GUTMANN: "Gutmann 35-pass method (legacy)"
        }
        return descriptions.get(pattern, f"Unknown pattern: {pattern}")
    
    @staticmethod
    def get_recommended_pattern(storage_type: str) -> WipePattern:
        """
        Get recommended wipe pattern based on storage type.
        
        Args:
            storage_type: Type of storage (hdd, ssd, flash, etc.)
            
        Returns:
            WipePattern: Recommended pattern for the storage type
        """
        storage_type = storage_type.lower()
        
        if storage_type in ['ssd', 'nvme', 'flash']:
            # For SSDs, single pass is usually sufficient due to wear leveling
            return WipePattern.NIST_CLEAR
        elif storage_type in ['hdd', 'hard_disk']:
            # For HDDs, multiple passes may be beneficial
            return WipePattern.NIST_PURGE
        else:
            # Default to NIST Clear for unknown types
            return WipePattern.NIST_CLEAR

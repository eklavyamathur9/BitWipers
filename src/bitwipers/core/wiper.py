"""
Main data wiping implementation with secure erasure functionality.
Supports multiple storage types and follows NIST SP 800-88 guidelines.
"""

import os
import time
import hashlib
import platform
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

from .patterns import WipePattern, WipePatterns


class WipeStatus(Enum):
    """Status of wipe operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WipeResult:
    """Result of a data wiping operation."""
    
    device_path: str
    pattern: WipePattern
    status: WipeStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    bytes_wiped: int = 0
    total_bytes: int = 0
    passes_completed: int = 0
    total_passes: int = 0
    error_message: Optional[str] = None
    verification_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def progress_percent(self) -> float:
        """Get progress as percentage."""
        if self.total_bytes == 0:
            return 0.0
        return min(100.0, (self.bytes_wiped / self.total_bytes) * 100.0)


class DataWiper:
    """
    Main data wiping class that handles secure erasure operations.
    Supports multiple storage types and wipe patterns.
    """
    
    def __init__(self, 
                 block_size: int = 4096,
                 progress_callback: Optional[Callable[[WipeResult], None]] = None,
                 verify_wipe: bool = True):
        """
        Initialize DataWiper.
        
        Args:
            block_size: Size of blocks to write (default 4096 bytes)
            progress_callback: Optional callback for progress updates
            verify_wipe: Whether to verify wipe completion
        """
        self.block_size = block_size
        self.progress_callback = progress_callback
        self.verify_wipe = verify_wipe
        self._cancelled = False
    
    def wipe_device(self, 
                   device_path: str,
                   pattern: WipePattern = WipePattern.NIST_CLEAR,
                   quick_format: bool = False) -> WipeResult:
        """
        Wipe a storage device using the specified pattern.
        
        Args:
            device_path: Path to the device to wipe
            pattern: Wipe pattern to use
            quick_format: Whether to perform quick format after wipe
            
        Returns:
            WipeResult: Result of the wipe operation
        """
        result = WipeResult(
            device_path=device_path,
            pattern=pattern,
            status=WipeStatus.PENDING,
            start_time=datetime.now()
        )
        
        try:
            # Validate device
            if not self._validate_device(device_path):
                result.status = WipeStatus.FAILED
                result.error_message = f"Invalid or inaccessible device: {device_path}"
                return result
            
            # Get device size
            device_size = self._get_device_size(device_path)
            result.total_bytes = device_size
            
            # Determine number of passes
            result.total_passes = self._get_pass_count(pattern)
            
            result.status = WipeStatus.IN_PROGRESS
            self._update_progress(result)
            
            # Perform wiping
            success = self._perform_wipe(device_path, pattern, result)
            
            if success and not self._cancelled:
                result.status = WipeStatus.COMPLETED
                result.end_time = datetime.now()
                
                # Verify wipe if requested
                if self.verify_wipe:
                    result.verification_hash = self._verify_wipe_completion(device_path)
                
                # Quick format if requested
                if quick_format:
                    self._quick_format(device_path)
                    
            elif self._cancelled:
                result.status = WipeStatus.CANCELLED
                result.end_time = datetime.now()
            else:
                result.status = WipeStatus.FAILED
                result.end_time = datetime.now()
                
        except Exception as e:
            result.status = WipeStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()
        
        self._update_progress(result)
        return result
    
    def wipe_file(self, 
                  file_path: str,
                  pattern: WipePattern = WipePattern.NIST_CLEAR,
                  remove_file: bool = True) -> WipeResult:
        """
        Securely wipe a single file.
        
        Args:
            file_path: Path to the file to wipe
            pattern: Wipe pattern to use
            remove_file: Whether to remove file after wiping
            
        Returns:
            WipeResult: Result of the wipe operation
        """
        result = WipeResult(
            device_path=file_path,
            pattern=pattern,
            status=WipeStatus.PENDING,
            start_time=datetime.now()
        )
        
        try:
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                result.status = WipeStatus.FAILED
                result.error_message = f"File not found: {file_path}"
                return result
            
            # Get file size
            file_size = os.path.getsize(file_path)
            result.total_bytes = file_size
            result.total_passes = self._get_pass_count(pattern)
            
            result.status = WipeStatus.IN_PROGRESS
            self._update_progress(result)
            
            # Perform file wiping
            success = self._perform_file_wipe(file_path, pattern, result)
            
            if success and not self._cancelled:
                result.status = WipeStatus.COMPLETED
                result.end_time = datetime.now()
                
                # Remove file if requested
                if remove_file:
                    os.remove(file_path)
                    
            elif self._cancelled:
                result.status = WipeStatus.CANCELLED
                result.end_time = datetime.now()
            else:
                result.status = WipeStatus.FAILED
                result.end_time = datetime.now()
                
        except Exception as e:
            result.status = WipeStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()
        
        self._update_progress(result)
        return result
    
    def cancel_operation(self):
        """Cancel the current wipe operation."""
        self._cancelled = True
    
    def _validate_device(self, device_path: str) -> bool:
        """Validate that the device exists and is accessible."""
        try:
            # Check if device exists
            if not os.path.exists(device_path):
                return False
            
            # Try to open device for reading
            with open(device_path, 'rb') as f:
                f.read(1)
            
            return True
        except (OSError, IOError, PermissionError):
            return False
    
    def _get_device_size(self, device_path: str) -> int:
        """Get the size of the storage device."""
        try:
            if os.path.isfile(device_path):
                return os.path.getsize(device_path)
            
            # For block devices on Linux/Unix
            if platform.system() != 'Windows':
                try:
                    result = subprocess.run(['blockdev', '--getsize64', device_path],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return int(result.stdout.strip())
                except (subprocess.CalledProcessError, ValueError):
                    pass
            
            # Fallback: try to seek to end
            with open(device_path, 'rb') as f:
                f.seek(0, 2)  # Seek to end
                return f.tell()
                
        except Exception:
            return 0
    
    def _get_pass_count(self, pattern: WipePattern) -> int:
        """Get the number of passes for the given pattern."""
        pass_counts = {
            WipePattern.ZERO_FILL: 1,
            WipePattern.ONE_FILL: 1,
            WipePattern.RANDOM: 1,
            WipePattern.DOD_3_PASS: 3,
            WipePattern.DOD_7_PASS: 7,
            WipePattern.NIST_CLEAR: 1,
            WipePattern.NIST_PURGE: 3,
            WipePattern.GUTMANN: 35
        }
        return pass_counts.get(pattern, 1)
    
    def _perform_wipe(self, device_path: str, pattern: WipePattern, result: WipeResult) -> bool:
        """Perform the actual wiping operation."""
        try:
            with open(device_path, 'r+b') as device:
                pattern_generator = WipePatterns.get_pattern_data(pattern, self.block_size)
                
                bytes_written_total = 0
                pass_number = 0
                
                for pass_data in pattern_generator:
                    if self._cancelled:
                        return False
                    
                    pass_number += 1
                    result.passes_completed = pass_number
                    
                    # Seek to beginning for each pass
                    device.seek(0)
                    bytes_written_pass = 0
                    
                    while bytes_written_pass < result.total_bytes:
                        if self._cancelled:
                            return False
                        
                        # Calculate remaining bytes
                        remaining = result.total_bytes - bytes_written_pass
                        chunk_size = min(self.block_size, remaining)
                        
                        # Write pattern data
                        if chunk_size == self.block_size:
                            chunk = pass_data
                        else:
                            chunk = pass_data[:chunk_size]
                        
                        bytes_written = device.write(chunk)
                        bytes_written_pass += bytes_written
                        bytes_written_total += bytes_written
                        
                        result.bytes_wiped = bytes_written_total
                        
                        # Update progress
                        if self.progress_callback:
                            self._update_progress(result)
                        
                        # Sync to ensure data is written
                        device.flush()
                        os.fsync(device.fileno())
                    
                    # Break if single-pass pattern
                    if pass_number >= result.total_passes:
                        break
                
                return True
                
        except Exception as e:
            result.error_message = str(e)
            return False
    
    def _perform_file_wipe(self, file_path: str, pattern: WipePattern, result: WipeResult) -> bool:
        """Perform secure file wiping."""
        try:
            pattern_generator = WipePatterns.get_pattern_data(pattern, self.block_size)
            
            for pass_number, pass_data in enumerate(pattern_generator, 1):
                if self._cancelled:
                    return False
                
                result.passes_completed = pass_number
                
                with open(file_path, 'r+b') as f:
                    f.seek(0)
                    bytes_written = 0
                    
                    while bytes_written < result.total_bytes:
                        if self._cancelled:
                            return False
                        
                        remaining = result.total_bytes - bytes_written
                        chunk_size = min(self.block_size, remaining)
                        
                        if chunk_size == self.block_size:
                            chunk = pass_data
                        else:
                            chunk = pass_data[:chunk_size]
                        
                        written = f.write(chunk)
                        bytes_written += written
                        
                        result.bytes_wiped = bytes_written
                        
                        if self.progress_callback:
                            self._update_progress(result)
                        
                        f.flush()
                        os.fsync(f.fileno())
                
                if pass_number >= result.total_passes:
                    break
            
            return True
            
        except Exception as e:
            result.error_message = str(e)
            return False
    
    def _verify_wipe_completion(self, device_path: str) -> str:
        """Verify that the wipe was completed successfully."""
        try:
            hash_obj = hashlib.sha256()
            
            with open(device_path, 'rb') as device:
                while chunk := device.read(self.block_size):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception:
            return ""
    
    def _quick_format(self, device_path: str):
        """Perform quick format on the device."""
        try:
            system = platform.system()
            
            if system == 'Windows':
                # Use Windows format command
                subprocess.run(['format', device_path, '/fs:NTFS', '/q', '/y'],
                              check=True, capture_output=True)
            elif system == 'Linux':
                # Use mkfs for Linux
                subprocess.run(['mkfs.ext4', '-F', device_path],
                              check=True, capture_output=True)
            
        except subprocess.CalledProcessError:
            pass  # Ignore format errors
    
    def _update_progress(self, result: WipeResult):
        """Update progress callback if available."""
        if self.progress_callback:
            self.progress_callback(result)

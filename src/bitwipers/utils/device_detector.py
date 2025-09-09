"""
Device detection utility for BitWipers.
Enumerates and validates storage devices across different platforms.
"""

import os
import platform
import subprocess
import psutil
from typing import List, Dict, Any, Optional
import json
import re


class DeviceDetector:
    """Detects and enumerates storage devices on the system."""
    
    def __init__(self):
        """Initialize the device detector."""
        self.system = platform.system()
        self.logger = None  # Will be set if logger is available
    
    def get_storage_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of storage devices available on the system.
        
        Returns:
            List[Dict[str, Any]]: List of device information dictionaries
        """
        devices = []
        
        try:
            if self.system == 'Windows':
                devices = self._get_windows_devices()
            elif self.system == 'Linux':
                devices = self._get_linux_devices()
            elif self.system == 'Darwin':  # macOS
                devices = self._get_macos_devices()
            else:
                # Fallback to psutil for unknown systems
                devices = self._get_psutil_devices()
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting devices: {e}")
            
        return devices
    
    def _get_windows_devices(self) -> List[Dict[str, Any]]:
        """Get storage devices on Windows using WMI and PowerShell."""
        devices = []
        
        try:
            # Use PowerShell to get disk information
            ps_command = """
            Get-WmiObject -Class Win32_DiskDrive | ForEach-Object {
                $disk = $_
                $partitions = Get-WmiObject -Query "ASSOCIATORS OF {Win32_DiskDrive.DeviceID='$($disk.DeviceID)'} WHERE AssocClass=Win32_DiskDriveToDiskPartition"
                
                [PSCustomObject]@{
                    DeviceID = $disk.DeviceID
                    Model = $disk.Model
                    Size = $disk.Size
                    MediaType = $disk.MediaType
                    InterfaceType = $disk.InterfaceType
                    SerialNumber = $disk.SerialNumber
                    Partitions = $partitions.Count
                }
            } | ConvertTo-Json -Depth 2
            """
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                disk_data = json.loads(result.stdout)
                
                # Handle both single disk and multiple disks
                if isinstance(disk_data, dict):
                    disk_data = [disk_data]
                
                for disk in disk_data:
                    if disk.get('Size'):
                        devices.append({
                            'name': disk.get('Model', 'Unknown Drive'),
                            'path': disk.get('DeviceID', ''),
                            'size': int(disk.get('Size', 0)),
                            'type': self._classify_device_type(disk.get('MediaType', '')),
                            'interface': disk.get('InterfaceType', 'Unknown'),
                            'serial': disk.get('SerialNumber', ''),
                            'partitions': disk.get('Partitions', 0)
                        })
                        
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
            # Fallback to basic drive enumeration
            drives = psutil.disk_partitions()
            for drive in drives:
                if drive.fstype:  # Only include drives with filesystem
                    try:
                        usage = psutil.disk_usage(drive.mountpoint)
                        devices.append({
                            'name': f"{drive.device} ({drive.fstype})",
                            'path': drive.device,
                            'size': usage.total,
                            'type': 'unknown',
                            'interface': 'unknown',
                            'serial': '',
                            'partitions': 1
                        })
                    except Exception:
                        continue
        
        return devices
    
    def _get_linux_devices(self) -> List[Dict[str, Any]]:
        """Get storage devices on Linux using various system tools."""
        devices = []
        
        # Try lsblk first (most reliable)
        devices = self._get_linux_lsblk_devices()
        
        # If lsblk failed, try /proc/partitions
        if not devices:
            devices = self._get_linux_proc_devices()
        
        # If still no devices, fallback to psutil
        if not devices:
            devices = self._get_psutil_devices()
        
        return devices
    
    def _get_linux_lsblk_devices(self) -> List[Dict[str, Any]]:
        """Get Linux devices using lsblk command."""
        devices = []
        
        try:
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,MODEL,SERIAL'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                for device in data.get('blockdevices', []):
                    if device.get('type') == 'disk':
                        size = self._parse_size_string(device.get('size', '0'))
                        
                        devices.append({
                            'name': device.get('model', device.get('name', 'Unknown')),
                            'path': f"/dev/{device.get('name')}",
                            'size': size,
                            'type': self._classify_device_type(device.get('name', '')),
                            'interface': 'unknown',
                            'serial': device.get('serial', ''),
                            'partitions': len(device.get('children', []))
                        })
                        
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return devices
    
    def _get_linux_proc_devices(self) -> List[Dict[str, Any]]:
        """Get Linux devices from /proc/partitions."""
        devices = []
        
        try:
            with open('/proc/partitions', 'r') as f:
                lines = f.readlines()[2:]  # Skip header
                
            seen_devices = set()
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 4:
                    major, minor, blocks, name = parts[:4]
                    
                    # Only include whole disks (not partitions)
                    if not re.search(r'\d+$', name) and name not in seen_devices:
                        seen_devices.add(name)
                        
                        size = int(blocks) * 1024  # blocks are in KB
                        device_path = f"/dev/{name}"
                        
                        if os.path.exists(device_path):
                            devices.append({
                                'name': name,
                                'path': device_path,
                                'size': size,
                                'type': self._classify_device_type(name),
                                'interface': 'unknown',
                                'serial': '',
                                'partitions': 0
                            })
                            
        except Exception:
            pass
        
        return devices
    
    def _get_macos_devices(self) -> List[Dict[str, Any]]:
        """Get storage devices on macOS using diskutil."""
        devices = []
        
        try:
            result = subprocess.run(
                ['diskutil', 'list', '-plist'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse diskutil output (would need plistlib for proper parsing)
                # For now, use a simpler approach
                lines = result.stdout.split('\n')
                for line in lines:
                    if '/dev/disk' in line and 'external' in line:
                        device_path = line.strip().split()[0]
                        
                        # Get device info
                        info_result = subprocess.run(
                            ['diskutil', 'info', device_path],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        if info_result.returncode == 0:
                            info_lines = info_result.stdout.split('\n')
                            size = 0
                            name = device_path
                            
                            for info_line in info_lines:
                                if 'Total Size:' in info_line:
                                    size_match = re.search(r'\((\d+)\s+Bytes\)', info_line)
                                    if size_match:
                                        size = int(size_match.group(1))
                                elif 'Device / Media Name:' in info_line:
                                    name = info_line.split(':', 1)[1].strip()
                            
                            devices.append({
                                'name': name,
                                'path': device_path,
                                'size': size,
                                'type': self._classify_device_type(device_path),
                                'interface': 'unknown',
                                'serial': '',
                                'partitions': 0
                            })
                            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return devices
    
    def _get_psutil_devices(self) -> List[Dict[str, Any]]:
        """Get devices using psutil as fallback."""
        devices = []
        
        try:
            partitions = psutil.disk_partitions(all=True)
            seen_devices = set()
            
            for partition in partitions:
                # Try to get the base device name
                device = partition.device
                if device not in seen_devices:
                    seen_devices.add(device)
                    
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        devices.append({
                            'name': f"{device} ({partition.fstype})",
                            'path': device,
                            'size': usage.total,
                            'type': 'unknown',
                            'interface': 'unknown',
                            'serial': '',
                            'partitions': 1
                        })
                    except Exception:
                        continue
                        
        except Exception:
            pass
        
        return devices
    
    def _classify_device_type(self, device_info: str) -> str:
        """Classify device type based on device information."""
        device_info = device_info.lower()
        
        if 'ssd' in device_info or 'solid state' in device_info:
            return 'SSD'
        elif 'nvme' in device_info:
            return 'NVMe'
        elif 'usb' in device_info or 'removable' in device_info:
            return 'USB'
        elif 'cd' in device_info or 'dvd' in device_info:
            return 'Optical'
        elif 'floppy' in device_info:
            return 'Floppy'
        else:
            return 'HDD'
    
    def _parse_size_string(self, size_str: str) -> int:
        """Parse size strings like '500G' or '1.5T' into bytes."""
        if not size_str:
            return 0
        
        size_str = size_str.upper().strip()
        
        # Extract number and unit
        match = re.match(r'^([\d.]+)([KMGT]?)B?$', size_str)
        if not match:
            return 0
        
        number = float(match.group(1))
        unit = match.group(2)
        
        multipliers = {
            '': 1,
            'K': 1024,
            'M': 1024**2,
            'G': 1024**3,
            'T': 1024**4
        }
        
        return int(number * multipliers.get(unit, 1))
    
    def validate_device(self, device_path: str) -> Dict[str, Any]:
        """
        Validate a device path and return device information.
        
        Args:
            device_path: Path to the device
            
        Returns:
            Dict with validation results and device info
        """
        result = {
            'valid': False,
            'exists': False,
            'readable': False,
            'writable': False,
            'size': 0,
            'type': 'unknown',
            'error': None
        }
        
        try:
            # Check if device exists
            result['exists'] = os.path.exists(device_path)
            if not result['exists']:
                result['error'] = f"Device {device_path} does not exist"
                return result
            
            # Check if readable
            try:
                with open(device_path, 'rb') as f:
                    f.read(1)
                result['readable'] = True
            except (IOError, PermissionError):
                result['error'] = f"Cannot read from {device_path}"
                return result
            
            # Check if writable (be very careful here)
            try:
                with open(device_path, 'r+b') as f:
                    f.seek(0)
                    # Don't actually write anything, just check if we can open for writing
                result['writable'] = True
            except (IOError, PermissionError):
                result['error'] = f"Cannot write to {device_path}"
                return result
            
            # Get device size
            try:
                if os.path.isfile(device_path):
                    result['size'] = os.path.getsize(device_path)
                else:
                    # For block devices, try different methods
                    if self.system == 'Linux':
                        # Use blockdev
                        try:
                            size_result = subprocess.run(
                                ['blockdev', '--getsize64', device_path],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if size_result.returncode == 0:
                                result['size'] = int(size_result.stdout.strip())
                        except Exception:
                            pass
                    
                    # Fallback: seek to end
                    if result['size'] == 0:
                        try:
                            with open(device_path, 'rb') as f:
                                f.seek(0, 2)  # Seek to end
                                result['size'] = f.tell()
                        except Exception:
                            pass
            except Exception as e:
                result['error'] = f"Cannot determine size of {device_path}: {e}"
                return result
            
            # Classify device type
            result['type'] = self._classify_device_type(device_path)
            
            result['valid'] = True
            
        except Exception as e:
            result['error'] = f"Error validating {device_path}: {e}"
        
        return result
    
    def is_system_device(self, device_path: str) -> bool:
        """
        Check if a device is likely to be a system/boot device.
        
        Args:
            device_path: Path to the device
            
        Returns:
            bool: True if device appears to be a system device
        """
        try:
            # Check if any partition is mounted as system directories
            if self.system == 'Windows':
                # Check if device contains C: drive
                drives = psutil.disk_partitions()
                for drive in drives:
                    if drive.device.startswith(device_path) and drive.mountpoint in ['C:\\', 'C:/']:
                        return True
            
            elif self.system in ['Linux', 'Darwin']:
                # Check if device contains root filesystem
                mounts = psutil.disk_partitions()
                for mount in mounts:
                    if (mount.device.startswith(device_path) and 
                        mount.mountpoint in ['/', '/boot', '/usr', '/var']):
                        return True
            
        except Exception:
            pass
        
        return False
    
    def get_device_info(self, device_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific device.
        
        Args:
            device_path: Path to the device
            
        Returns:
            Dict with detailed device information
        """
        # Start with validation
        info = self.validate_device(device_path)
        
        if not info['valid']:
            return info
        
        # Add additional information
        try:
            # Check if it's a system device
            info['is_system_device'] = self.is_system_device(device_path)
            
            # Get filesystem information if applicable
            partitions = psutil.disk_partitions()
            for partition in partitions:
                if partition.device.startswith(device_path):
                    info['filesystem'] = partition.fstype
                    info['mountpoint'] = partition.mountpoint
                    break
            
            # Format size for display
            info['size_formatted'] = self._format_bytes(info['size'])
            
        except Exception as e:
            info['warning'] = f"Could not get additional info: {e}"
        
        return info
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format byte count for human readability."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"

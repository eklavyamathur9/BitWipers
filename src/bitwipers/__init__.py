"""
BitWipers - Secure Data Wiping for Trustworthy IT Asset Recycling

A cross-platform data wiping application designed to address India's e-waste crisis
by providing trustworthy data sanitization for IT asset recycling.
"""

__version__ = "1.0.0"
__author__ = "Ministry of Mines - JNARDDC"
__license__ = "MIT"

# Import main components
from .core import DataWiper, WipePattern
from .crypto import CertificateGenerator
from .utils import DeviceDetector, Logger

__all__ = [
    "DataWiper",
    "WipePattern", 
    "CertificateGenerator",
    "DeviceDetector",
    "Logger",
]

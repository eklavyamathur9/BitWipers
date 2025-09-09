# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

BitWipers is a secure data wiping application for trustworthy IT asset recycling. It provides NIST SP 800-88 compliant data erasure with tamper-proof certificates to combat India's e-waste crisis. The application supports Windows, Linux, and Android platforms with both GUI and CLI interfaces.

## Development Commands

### Setup & Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"

# Install with all extras (dev + docs)
pip install -e ".[dev,docs]"
```

### Running the Application
```bash
# Launch GUI (default)
python src/bitwipers/main.py

# Launch CLI
python src/bitwipers/main.py --cli

# CLI specific commands
python -m bitwipers.cli.main list-devices
python -m bitwipers.cli.main list-patterns
python -m bitwipers.cli.main info <device_path>

# Run with specific log level
python src/bitwipers/main.py --log-level DEBUG --log-file wipe.log
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bitwipers --cov-report=html

# Run specific test files
pytest tests/test_patterns.py
pytest tests/test_wiper.py

# Run tests with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests  
pytest tests/integration/
```

### Code Quality
```bash
# Format code with Black
black src/ tests/ --line-length 88

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/bitwipers/

# Run all quality checks
black src/ tests/ && flake8 src/ tests/ && mypy src/bitwipers/
```

### Building & Distribution
```bash
# Build package
python setup.py sdist bdist_wheel

# Install locally
pip install .

# Install in development mode
pip install -e .

# Build documentation
cd docs && sphinx-build -b html . _build/html
```

## Architecture Overview

### Core Modules

#### Data Wiping Engine (`src/bitwipers/core/`)
- **`wiper.py`**: Main `DataWiper` class that orchestrates the wiping process
  - Handles device validation, progress tracking, and verification
  - Supports both device and file wiping
  - Implements cancellation and error recovery
  - Returns `WipeResult` with complete operation metadata

- **`patterns.py`**: Implementation of various wiping patterns
  - `WipePattern` enum defines supported patterns (NIST, DoD, Gutmann)
  - `WipePatterns` class generates pattern data streams
  - Recommends optimal patterns based on storage type (SSD vs HDD)
  - Implements NIST SP 800-88 Clear and Purge methods

#### Certificate System (`src/bitwipers/crypto/`)
- **`certificate.py`**: Tamper-proof certificate generation
  - `CertificateGenerator` creates digitally signed certificates
  - RSA key generation and management
  - Outputs both JSON and PDF formats
  - Includes verification hashes and digital signatures
  - Compliant with NIST SP 800-88 reporting requirements

#### User Interfaces

- **GUI (`src/bitwipers/gui/main_window.py`)**:
  - Tkinter-based interface for general users
  - Device selection with automatic enumeration
  - Real-time progress monitoring
  - One-click secure wiping
  - Certificate generation and saving

- **CLI (`src/bitwipers/cli/main.py`)**:
  - Click-based command-line interface
  - Commands: `list-devices`, `list-patterns`, `wipe`, `info`
  - Progress callbacks during wiping
  - Automatic certificate generation

#### Utilities (`src/bitwipers/utils/`)
- **`device_detector.py`**: Cross-platform device enumeration
  - Windows: Uses WMI/PowerShell for device info
  - Linux: Uses lsblk and /proc/partitions
  - Falls back to psutil for compatibility
  - Validates device accessibility and type

- **`logger.py`**: Centralized logging system
  - Configurable log levels
  - File and console output
  - Structured logging for audit trails

### Data Flow

1. **Device Detection**: `DeviceDetector` enumerates available storage devices
2. **User Selection**: GUI/CLI presents devices, user selects target
3. **Validation**: System validates device is accessible and not system-critical
4. **Pattern Selection**: User chooses wipe pattern (defaults to NIST Clear)
5. **Wiping Process**:
   - `DataWiper` reads pattern data from `WipePatterns`
   - Writes pattern blocks to device in chunks
   - Tracks progress and updates UI via callbacks
   - Optionally verifies wipe completion
6. **Certificate Generation**: 
   - `CertificateGenerator` creates signed certificate from `WipeResult`
   - Saves as PDF/JSON with digital signature
7. **Verification**: Third parties can verify certificate authenticity

### Key Design Patterns

- **Strategy Pattern**: Wipe patterns are interchangeable algorithms
- **Observer Pattern**: Progress callbacks notify UI of wipe status
- **Factory Pattern**: Pattern generation based on storage type
- **Builder Pattern**: Certificate construction from wipe results

## Critical Considerations

### Security Requirements
- Application requires administrator/root privileges for direct disk access
- All operations must validate target device to prevent system damage
- Cryptographic operations use `secrets` module for secure randomness
- Certificates include tamper-evident digital signatures

### Platform-Specific Handling
- **Windows**: Requires PowerShell for WMI access, handles drive letters
- **Linux**: Uses `/dev/` paths, requires sudo for raw device access
- **Android**: Special handling for internal/external storage (future implementation)

### Performance Optimization
- Block-based I/O with configurable chunk sizes (default 4096 bytes)
- Asynchronous progress updates to prevent UI freezing
- Efficient pattern generation using iterators
- SSD-aware patterns to minimize unnecessary writes

### Error Recovery
- Graceful handling of device disconnection
- Partial wipe recovery and reporting
- Detailed error messages in `WipeResult`
- Automatic fallback methods for device detection

## Standards Compliance

The application follows these standards:
- **NIST SP 800-88 Rev. 1**: Media Sanitization Guidelines
  - Clear: Logical techniques on user-addressable storage
  - Purge: Physical/logical techniques including hidden areas
  - Implements recommended verification procedures

- **DoD 5220.22-M**: Department of Defense clearing standard
  - 3-pass and 7-pass implementations
  - Pattern verification between passes

## Module Dependencies

```
bitwipers.main
├── bitwipers.gui.main_window
│   ├── bitwipers.core.wiper
│   ├── bitwipers.core.patterns
│   ├── bitwipers.crypto.certificate
│   └── bitwipers.utils.device_detector
├── bitwipers.cli.main
│   ├── bitwipers.core.wiper
│   ├── bitwipers.core.patterns
│   ├── bitwipers.crypto.certificate
│   └── bitwipers.utils.device_detector
└── bitwipers.utils.logger

bitwipers.crypto.certificate
├── cryptography (external)
├── reportlab (external)
└── bitwipers.core.wiper

bitwipers.utils.device_detector
└── psutil (external)
```

## Common Development Tasks

### Adding a New Wipe Pattern
1. Add enum value to `WipePattern` in `src/bitwipers/core/patterns.py`
2. Implement pattern generator method in `WipePatterns` class
3. Add description in `get_pattern_description()`
4. Update UI components to include new pattern option
5. Add tests for pattern generation and validation

### Supporting a New Platform
1. Add platform detection in `DeviceDetector.__init__()`
2. Implement `_get_<platform>_devices()` method
3. Add platform-specific device validation
4. Update GUI/CLI for platform-specific features
5. Test device enumeration and wiping

### Extending Certificate Format
1. Update `WipeCertificate` dataclass with new fields
2. Modify `generate_certificate()` to populate fields
3. Update PDF generation in `_generate_pdf_certificate()`
4. Ensure backward compatibility with verification
5. Update certificate validation logic

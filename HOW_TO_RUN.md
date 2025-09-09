# 🚀 How to Run BitWipers

## Prerequisites
- Python 3.8 or higher installed
- Administrator privileges (for disk operations)

## Step 1: Set Up Python Environment

### Option A: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Or for Command Prompt
venv\Scripts\activate.bat
```

### Option B: Use Global Python
Skip virtual environment and use your system Python directly.

## Step 2: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

If you get errors, try installing packages individually:
```bash
pip install cryptography
pip install reportlab
pip install psutil
pip install click
```

## Step 3: Run the Application

### 🖥️ GUI Mode (Default - Easiest)
```bash
# From project root directory
python src/bitwipers/main.py
```
Or:
```bash
python src/bitwipers/main.py --gui
```

### 💻 CLI Mode (Command Line)
```bash
# Show help
python src/bitwipers/main.py --cli --help

# Or run CLI directly
python src/bitwipers/cli/main.py --help

# List available devices
python -m bitwipers.cli.main list-devices

# List wipe patterns
python -m bitwipers.cli.main list-patterns
```

### 📝 With Logging
```bash
# Run with debug logging
python src/bitwipers/main.py --log-level DEBUG

# Save logs to file
python src/bitwipers/main.py --log-file wipe_log.txt
```

## Quick Test Commands

### 1. Test if Python works:
```bash
python --version
```

### 2. Test imports:
```bash
python -c "import sys; sys.path.insert(0, 'src'); from bitwipers.core.patterns import WipePattern; print('✅ Imports working')"
```

### 3. Run help:
```bash
python src/bitwipers/main.py --help
```

## 🎯 Step-by-Step for Windows

1. **Open PowerShell as Administrator**
   - Right-click on PowerShell
   - Select "Run as Administrator"

2. **Navigate to project folder**
   ```powershell
   cd "D:\GEN AI\BitWipers"
   ```

3. **Create and activate virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   If you get an execution policy error:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Install dependencies**
   ```powershell
   pip install cryptography reportlab psutil click
   ```

5. **Run the GUI**
   ```powershell
   python src\bitwipers\main.py
   ```

## 🎨 What You'll See

### GUI Mode:
- A window will open with:
  - Device selection dropdown
  - Wipe pattern selection
  - Start Wipe button
  - Progress bar
  - Certificate generation options

### CLI Mode:
- Command-line interface with:
  - Device listing
  - Pattern options
  - Text-based progress
  - Certificate generation

## ⚠️ Important Safety Notes

1. **WARNING**: This tool performs IRREVERSIBLE data destruction
2. **Always** verify the target device before wiping
3. **Run as Administrator** for disk access permissions
4. **Test on non-critical devices first**

## 🔧 Troubleshooting

### "Module not found" error:
```bash
# Make sure you're in the project root
cd "D:\GEN AI\BitWipers"

# Add src to Python path
set PYTHONPATH=%PYTHONPATH%;D:\GEN AI\BitWipers\src
```

### "Permission denied" error:
- Run PowerShell/Command Prompt as Administrator
- On Windows, right-click → "Run as Administrator"

### GUI doesn't open:
- Install tkinter (usually comes with Python)
- Try CLI mode instead: `python src/bitwipers/main.py --cli`

### Import errors:
```bash
# Install in development mode
pip install -e .
```

## 🚦 Quick Start (Copy & Paste)

```powershell
# Complete setup and run (PowerShell)
cd "D:\GEN AI\BitWipers"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install cryptography reportlab psutil click
python src\bitwipers\main.py
```

## 📱 Testing Without Real Devices

For safe testing without wiping real devices:

1. **Create a test file:**
   ```python
   # Create test_wipe.py
   with open("test_file.bin", "wb") as f:
       f.write(b"Test data" * 1000)
   ```

2. **Wipe the test file:**
   ```bash
   python src/bitwipers/cli/main.py wipe test_file.bin --pattern zero_fill
   ```

## 🎯 Expected Output

### Successful GUI Launch:
- Window opens with "BitWipers - Secure Data Wiping System" title
- Device list populated
- All buttons clickable

### Successful CLI Run:
```
BitWipers CLI - Secure Data Wiping for Trustworthy IT Asset Recycling
Usage: main.py [OPTIONS] COMMAND [ARGS]...
Commands:
  list-devices   List available storage devices
  list-patterns  List available wipe patterns
  wipe          Wipe a storage device or file
```

---

## Need Help?

1. Check error messages carefully
2. Ensure Python 3.8+ is installed
3. Run as Administrator
4. Try CLI mode if GUI fails
5. Check `WARP.md` for development details

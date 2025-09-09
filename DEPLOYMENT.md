# BitWipers Deployment Guide

## 📦 Deployment Options

### 1. PyPI Deployment (Python Package Index)

#### Prerequisites:
- PyPI account at https://pypi.org
- Test PyPI account at https://test.pypi.org (recommended for testing)

#### Setup PyPI Token:
1. Login to PyPI → Account Settings → API tokens
2. Create a new API token with scope "Entire account" or specific to "bitwipers"
3. Save the token securely (starts with `pypi-`)

#### Manual Deployment to PyPI:
```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the distribution
twine check dist/*

# Upload to Test PyPI first (recommended)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

#### Automated Deployment via GitHub Actions:
1. Add PyPI token to GitHub Secrets:
   - Go to Repository → Settings → Secrets → Actions
   - Add secret named `PYPI_API_TOKEN` with your token

2. Create a release on GitHub:
   - Go to Releases → Create a new release
   - Tag version: `v1.0.0` (semantic versioning)
   - Release title: `BitWipers v1.0.0`
   - The CI/CD pipeline will automatically deploy to PyPI

### 2. GitHub Releases

#### Creating a Release:
1. Go to your repository on GitHub
2. Click "Releases" → "Draft a new release"
3. Choose a tag (create new: `v1.0.0`)
4. Release title: `BitWipers v1.0.0 - Initial Release`
5. Describe the release features
6. Attach binary files if needed
7. Publish release

#### Release Assets (Automated):
The GitHub Actions workflow automatically:
- Builds wheel and source distributions
- Attaches them to the release
- Deploys to PyPI if configured

### 3. Docker Deployment

Create a `Dockerfile` in the root directory:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY setup.py .
COPY README.md .

# Install the application
RUN pip install .

# Run as non-root user
RUN useradd -m -u 1000 bitwipers && chown -R bitwipers:bitwipers /app
USER bitwipers

# Default command
CMD ["bitwipers", "--help"]
```

Build and push to Docker Hub:
```bash
# Build image
docker build -t your-username/bitwipers:latest .

# Test locally
docker run -it --rm your-username/bitwipers:latest

# Push to Docker Hub
docker login
docker push your-username/bitwipers:latest
```

### 4. Standalone Executable (PyInstaller)

#### Create standalone executable:
```bash
# Install PyInstaller
pip install pyinstaller

# Create single executable file
pyinstaller --onefile --name bitwipers src/bitwipers/main.py

# Or create a folder with all dependencies
pyinstaller --onedir --name bitwipers src/bitwipers/main.py

# The executable will be in dist/bitwipers/
```

#### Create spec file for advanced configuration:
```python
# bitwipers.spec
a = Analysis(
    ['src/bitwipers/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/bitwipers/assets', 'assets'),
    ],
    hiddenimports=['tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BitWipers',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
```

### 5. Linux Package (DEB/RPM)

#### Create DEB package:
```bash
# Install tools
pip install stdeb

# Generate debian source package
python setup.py --command-packages=stdeb.command sdist_dsc

# Build DEB package
cd deb_dist/bitwipers-1.0.0
dpkg-buildpackage -rfakeroot -uc -us
```

#### Create RPM package:
```bash
# Install tools
pip install pyp2rpm

# Generate RPM spec
pyp2rpm bitwipers > bitwipers.spec

# Build RPM
rpmbuild -ba bitwipers.spec
```

### 6. Bootable ISO Creation

For creating bootable media for offline wiping:

```bash
# Create a custom Linux ISO with BitWipers
# This requires a Linux build environment

# 1. Start with a minimal Linux distribution (e.g., Alpine Linux)
# 2. Add Python and BitWipers
# 3. Configure auto-start
# 4. Build ISO

# Example using mkisofs:
mkisofs -o bitwipers.iso \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R -V "BitWipers Boot" \
    ./iso_root/
```

## 🚀 Continuous Deployment

### GitHub Actions Deployment Pipeline

The `.github/workflows/ci.yml` file includes:
1. **Testing**: Runs on every push/PR
2. **Building**: Creates distributions
3. **Deployment**: Triggers on release creation

### Version Management

Use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

Update version in:
1. `setup.py`
2. `pyproject.toml`
3. `src/bitwipers/__init__.py`
4. Create git tag: `git tag v1.0.0`

## 📱 Platform-Specific Deployment

### Windows
- Create MSI installer using `cx_Freeze` or `py2exe`
- Sign executable with code signing certificate
- Distribute via Microsoft Store (optional)

### macOS
- Create DMG file
- Sign with Apple Developer certificate
- Notarize for Gatekeeper
- Distribute via Mac App Store (optional)

### Android (Future)
- Package with Kivy or BeeWare
- Create APK
- Distribute via Google Play Store

## 🔒 Security Considerations

1. **Code Signing**: Sign releases with GPG
   ```bash
   gpg --sign --detach-sign --armor dist/bitwipers-1.0.0.tar.gz
   ```

2. **Checksum Files**: Provide SHA256 checksums
   ```bash
   sha256sum dist/* > SHA256SUMS
   ```

3. **Vulnerability Scanning**: Use safety and bandit
   ```bash
   safety check
   bandit -r src/
   ```

## 📊 Monitoring

### PyPI Statistics
- View download statistics at https://pypistats.org/packages/bitwipers

### GitHub Insights
- Repository → Insights → Traffic
- Track clones, views, and popular content

## 🆘 Troubleshooting

### Common Issues:

1. **PyPI Upload Failed**:
   - Check token permissions
   - Verify package name availability
   - Ensure version number is incremented

2. **GitHub Actions Failed**:
   - Check workflow syntax
   - Verify secrets are set
   - Review action logs

3. **Docker Build Failed**:
   - Check Dockerfile syntax
   - Verify base image availability
   - Ensure all files are included

## 📚 Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)

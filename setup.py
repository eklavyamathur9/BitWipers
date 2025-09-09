"""
BitWipers - Secure Data Wiping for Trustworthy IT Asset Recycling
Setup configuration for the Python package.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="bitwipers",
    version="1.0.0",
    author="Ministry of Mines - JNARDDC",
    author_email="support@bitwipers.gov.in",
    description="Secure data wiping application for trustworthy IT asset recycling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ministry-of-mines/BitWipers",
    project_urls={
        "Bug Tracker": "https://github.com/ministry-of-mines/BitWipers/issues",
        "Documentation": "https://bitwipers.readthedocs.io/",
        "Source Code": "https://github.com/ministry-of-mines/BitWipers",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Systems Administration",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Android",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
        "reportlab>=4.0.0",
        "psutil>=5.9.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bitwipers=bitwipers.main:main",
            "bitwipers-gui=bitwipers.gui.main:main",
            "bitwipers-cli=bitwipers.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "data-wiping",
        "secure-erasure",
        "data-sanitization",
        "e-waste",
        "IT-asset-recycling",
        "NIST-SP-800-88",
        "digital-certificates",
        "cross-platform",
        "security",
    ],
    platforms=["Windows", "Linux", "Android"],
)

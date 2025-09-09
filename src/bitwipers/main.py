"""
Main entry point for BitWipers application.
Provides both GUI and CLI interfaces.
"""

import sys
import argparse
from pathlib import Path

from .utils.logger import setup_logging
from .core.patterns import WipePattern


def main():
    """Main entry point for BitWipers application."""
    parser = argparse.ArgumentParser(
        description="BitWipers - Secure Data Wiping for Trustworthy IT Asset Recycling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bitwipers                           # Launch GUI
  bitwipers --gui                     # Launch GUI explicitly
  bitwipers --cli --help             # Show CLI help
  bitwipers --version                 # Show version

For more information, visit: https://github.com/ministry-of-mines/BitWipers
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='BitWipers 1.0.0'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch GUI interface (default)'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Launch CLI interface'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file (optional)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(
        log_level=args.log_level,
        log_file=args.log_file,
        enable_console=True
    )
    
    logger.info("BitWipers application starting")
    
    try:
        if args.cli:
            # Launch CLI interface
            from .cli.main import main as cli_main
            cli_main()
        else:
            # Launch GUI interface (default)
            from .gui.main_window import main as gui_main
            gui_main()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

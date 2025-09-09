"""
Command Line Interface for BitWipers.
Basic CLI implementation for future expansion.
"""

import click
from pathlib import Path

from ..core.wiper import DataWiper, WipePattern
from ..core.patterns import WipePatterns
from ..crypto.certificate import CertificateGenerator
from ..utils.device_detector import DeviceDetector
from ..utils.logger import get_logger


@click.group()
@click.version_option(version="1.0.0", prog_name="BitWipers CLI")
def cli():
    """BitWipers CLI - Secure Data Wiping for Trustworthy IT Asset Recycling."""
    pass


@cli.command()
def list_devices():
    """List available storage devices."""
    detector = DeviceDetector()
    devices = detector.get_storage_devices()
    
    if not devices:
        click.echo("No storage devices found.")
        return
    
    click.echo("Available Storage Devices:")
    click.echo("=" * 50)
    
    for i, device in enumerate(devices, 1):
        click.echo(f"{i}. {device['name']}")
        click.echo(f"   Path: {device['path']}")
        click.echo(f"   Size: {_format_bytes(device['size'])}")
        click.echo(f"   Type: {device['type']}")
        click.echo()


@cli.command()
def list_patterns():
    """List available wipe patterns."""
    click.echo("Available Wipe Patterns:")
    click.echo("=" * 40)
    
    for pattern in WipePattern:
        description = WipePatterns.get_pattern_description(pattern)
        click.echo(f"• {pattern.value}")
        click.echo(f"  {description}")
        click.echo()


@cli.command()
@click.argument('device_path', type=click.Path())
@click.option('--pattern', default='nist_clear', 
              type=click.Choice([p.value for p in WipePattern]),
              help='Wipe pattern to use (default: nist_clear)')
@click.option('--verify/--no-verify', default=True,
              help='Verify wipe completion (default: True)')
@click.option('--certificate/--no-certificate', default=True,
              help='Generate certificate (default: True)')
@click.option('--cert-output', type=click.Path(),
              help='Certificate output file (PDF or JSON)')
@click.confirmation_option(
    prompt='This will permanently destroy all data. Are you sure?'
)
def wipe(device_path, pattern, verify, certificate, cert_output):
    """Wipe a storage device or file."""
    logger = get_logger()
    
    # Validate device
    detector = DeviceDetector()
    validation = detector.validate_device(device_path)
    
    if not validation['valid']:
        click.echo(f"Error: {validation['error']}", err=True)
        return 1
    
    # Get pattern
    try:
        wipe_pattern = WipePattern(pattern)
    except ValueError:
        click.echo(f"Error: Invalid pattern '{pattern}'", err=True)
        return 1
    
    # Setup progress callback
    def progress_callback(result):
        progress = result.progress_percent
        click.echo(f"Progress: {progress:.1f}% - Pass {result.passes_completed}/{result.total_passes}")
    
    # Create wiper
    wiper = DataWiper(
        progress_callback=progress_callback,
        verify_wipe=verify
    )
    
    click.echo(f"Starting wipe of {device_path} with pattern {pattern}...")
    
    # Perform wipe
    if Path(device_path).is_file():
        result = wiper.wipe_file(device_path, wipe_pattern)
    else:
        result = wiper.wipe_device(device_path, wipe_pattern)
    
    # Show results
    if result.status.value == 'completed':
        click.echo("✅ Wipe completed successfully!")
        click.echo(f"Duration: {result.duration:.2f} seconds")
        click.echo(f"Bytes wiped: {_format_bytes(result.bytes_wiped)}")
        
        # Generate certificate
        if certificate:
            try:
                cert_gen = CertificateGenerator()
                cert = cert_gen.generate_certificate(result)
                
                if cert_output:
                    output_path = cert_output
                else:
                    # Default certificate path
                    output_path = f"bitwipers_certificate_{cert.certificate_id}.pdf"
                
                # Save certificate
                if output_path.endswith('.json'):
                    success = cert_gen.save_certificate_json(cert, output_path)
                else:
                    success = cert_gen.save_certificate_pdf(cert, output_path)
                
                if success:
                    click.echo(f"📜 Certificate saved: {output_path}")
                else:
                    click.echo("⚠️  Failed to save certificate", err=True)
                    
            except Exception as e:
                click.echo(f"⚠️  Certificate generation failed: {e}", err=True)
        
        return 0
    else:
        click.echo("❌ Wipe failed!")
        if result.error_message:
            click.echo(f"Error: {result.error_message}", err=True)
        return 1


@cli.command()
@click.argument('device_path', type=click.Path(exists=True))
def info(device_path):
    """Show detailed information about a device or file."""
    detector = DeviceDetector()
    info = detector.get_device_info(device_path)
    
    click.echo(f"Device Information: {device_path}")
    click.echo("=" * 50)
    
    if info['valid']:
        click.echo(f"Valid: ✅ Yes")
        click.echo(f"Size: {_format_bytes(info['size'])}")
        click.echo(f"Type: {info['type']}")
        click.echo(f"Readable: {'✅' if info['readable'] else '❌'}")
        click.echo(f"Writable: {'✅' if info['writable'] else '❌'}")
        
        if 'is_system_device' in info:
            system_status = "⚠️  Yes (System Device)" if info['is_system_device'] else "✅ No"
            click.echo(f"System Device: {system_status}")
        
        if 'filesystem' in info:
            click.echo(f"Filesystem: {info['filesystem']}")
        
        if 'mountpoint' in info:
            click.echo(f"Mount Point: {info['mountpoint']}")
            
    else:
        click.echo(f"Valid: ❌ No")
        click.echo(f"Error: {info['error']}")


def _format_bytes(bytes_count: int) -> str:
    """Format byte count for human readability."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()

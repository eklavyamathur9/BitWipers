"""
Certificate generation system for BitWipers.
Creates tamper-proof, digitally signed certificates for wipe operations.
"""

import json
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from ..core.wiper import WipeResult


@dataclass
class WipeCertificate:
    """Data structure for wipe certificates."""
    
    certificate_id: str
    device_path: str
    device_serial: Optional[str]
    device_model: Optional[str]
    device_size_bytes: int
    wipe_pattern: str
    wipe_start_time: str
    wipe_end_time: str
    wipe_duration_seconds: float
    bytes_wiped: int
    passes_completed: int
    verification_hash: Optional[str]
    status: str
    operator: str
    organization: str
    nist_compliance: str
    certificate_hash: str
    digital_signature: str
    created_at: str
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert certificate to dictionary."""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert certificate to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class CertificateGenerator:
    """Generates tamper-proof wipe certificates in PDF and JSON formats."""
    
    def __init__(self, 
                 private_key_path: Optional[str] = None,
                 organization: str = "Ministry of Mines - JNARDDC",
                 operator: str = "BitWipers System"):
        """
        Initialize certificate generator.
        
        Args:
            private_key_path: Path to RSA private key for signing
            organization: Organization name for certificates
            operator: Operator name for certificates
        """
        self.organization = organization
        self.operator = operator
        
        # Load or generate private key for signing
        if private_key_path and Path(private_key_path).exists():
            self.private_key = self._load_private_key(private_key_path)
        else:
            self.private_key = self._generate_private_key()
        
        self.public_key = self.private_key.public_key()
    
    def generate_certificate(self, wipe_result: WipeResult, 
                           device_info: Optional[Dict[str, str]] = None) -> WipeCertificate:
        """
        Generate a wipe certificate from WipeResult.
        
        Args:
            wipe_result: Result of the wipe operation
            device_info: Additional device information
            
        Returns:
            WipeCertificate: Generated certificate
        """
        device_info = device_info or {}
        
        # Generate unique certificate ID
        cert_id = self._generate_certificate_id()
        
        # Create certificate data
        cert_data = WipeCertificate(
            certificate_id=cert_id,
            device_path=wipe_result.device_path,
            device_serial=device_info.get('serial_number'),
            device_model=device_info.get('model'),
            device_size_bytes=wipe_result.total_bytes,
            wipe_pattern=wipe_result.pattern.value,
            wipe_start_time=wipe_result.start_time.isoformat(),
            wipe_end_time=wipe_result.end_time.isoformat() if wipe_result.end_time else "",
            wipe_duration_seconds=wipe_result.duration,
            bytes_wiped=wipe_result.bytes_wiped,
            passes_completed=wipe_result.passes_completed,
            verification_hash=wipe_result.verification_hash,
            status=wipe_result.status.value,
            operator=self.operator,
            organization=self.organization,
            nist_compliance="NIST SP 800-88 Rev. 1",
            certificate_hash="",  # Will be calculated
            digital_signature="",  # Will be calculated
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        # Calculate certificate hash
        cert_dict = cert_data.to_dict()
        cert_dict.pop('certificate_hash', None)
        cert_dict.pop('digital_signature', None)
        
        cert_json = json.dumps(cert_dict, sort_keys=True)
        cert_hash = hashlib.sha256(cert_json.encode()).hexdigest()
        cert_data.certificate_hash = cert_hash
        
        # Generate digital signature
        signature = self._sign_data(cert_hash.encode())
        cert_data.digital_signature = signature.hex()
        
        return cert_data
    
    def save_certificate_json(self, certificate: WipeCertificate, 
                             output_path: str) -> bool:
        """
        Save certificate as JSON file.
        
        Args:
            certificate: Certificate to save
            output_path: Output file path
            
        Returns:
            bool: Success status
        """
        try:
            with open(output_path, 'w') as f:
                f.write(certificate.to_json())
            return True
        except Exception:
            return False
    
    def save_certificate_pdf(self, certificate: WipeCertificate, 
                            output_path: str) -> bool:
        """
        Save certificate as PDF file.
        
        Args:
            certificate: Certificate to save
            output_path: Output file path
            
        Returns:
            bool: Success status
        """
        try:
            self._generate_pdf_certificate(certificate, output_path)
            return True
        except Exception:
            return False
    
    def verify_certificate(self, certificate: WipeCertificate) -> bool:
        """
        Verify certificate authenticity and integrity.
        
        Args:
            certificate: Certificate to verify
            
        Returns:
            bool: True if certificate is valid
        """
        try:
            # Recreate certificate hash
            cert_dict = certificate.to_dict()
            original_hash = cert_dict.pop('certificate_hash', '')
            original_signature = cert_dict.pop('digital_signature', '')
            
            # Calculate expected hash
            cert_json = json.dumps(cert_dict, sort_keys=True)
            expected_hash = hashlib.sha256(cert_json.encode()).hexdigest()
            
            # Verify hash matches
            if original_hash != expected_hash:
                return False
            
            # Verify digital signature
            signature_bytes = bytes.fromhex(original_signature)
            return self._verify_signature(expected_hash.encode(), signature_bytes)
            
        except Exception:
            return False
    
    def _generate_certificate_id(self) -> str:
        """Generate unique certificate ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(4).upper()
        return f"BW-{timestamp}-{random_part}"
    
    def _load_private_key(self, key_path: str) -> rsa.RSAPrivateKey:
        """Load private key from file."""
        with open(key_path, 'rb') as f:
            private_key = load_pem_private_key(f.read(), password=None)
        return private_key
    
    def _generate_private_key(self) -> rsa.RSAPrivateKey:
        """Generate new RSA private key."""
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
    
    def _sign_data(self, data: bytes) -> bytes:
        """Sign data with private key."""
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    def _verify_signature(self, data: bytes, signature: bytes) -> bool:
        """Verify signature with public key."""
        try:
            self.public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def _generate_pdf_certificate(self, certificate: WipeCertificate, output_path: str):
        """Generate PDF certificate document."""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Title
        title = Paragraph("BitWipers Data Wipe Certificate", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Certificate header info
        header_data = [
            ['Certificate ID:', certificate.certificate_id],
            ['Organization:', certificate.organization],
            ['Created:', certificate.created_at[:19].replace('T', ' ')],
            ['NIST Compliance:', certificate.nist_compliance],
        ]
        
        header_table = Table(header_data, colWidths=[120, 300])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Device information
        story.append(Paragraph("Device Information", heading_style))
        device_data = [
            ['Device Path:', certificate.device_path],
            ['Serial Number:', certificate.device_serial or 'N/A'],
            ['Model:', certificate.device_model or 'N/A'],
            ['Size (bytes):', f"{certificate.device_size_bytes:,}"],
            ['Size (GB):', f"{certificate.device_size_bytes / (1024**3):.2f}"],
        ]
        
        device_table = Table(device_data, colWidths=[120, 300])
        device_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(device_table)
        story.append(Spacer(1, 20))
        
        # Wipe operation details\n        story.append(Paragraph("Wipe Operation Details", heading_style))
        wipe_data = [
            ['Wipe Pattern:', certificate.wipe_pattern],
            ['Start Time:', certificate.wipe_start_time[:19].replace('T', ' ')],
            ['End Time:', certificate.wipe_end_time[:19].replace('T', ' ') if certificate.wipe_end_time else 'N/A'],
            ['Duration:', f"{certificate.wipe_duration_seconds:.2f} seconds"],
            ['Bytes Wiped:', f"{certificate.bytes_wiped:,}"],
            ['Passes Completed:', str(certificate.passes_completed)],
            ['Status:', certificate.status.upper()],
        ]
        
        wipe_table = Table(wipe_data, colWidths=[120, 300])
        wipe_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(wipe_table)
        story.append(Spacer(1, 20))
        
        # Verification information
        story.append(Paragraph("Verification", heading_style))
        verification_data = [
            ['Verification Hash:', certificate.verification_hash or 'N/A'],
            ['Certificate Hash:', certificate.certificate_hash],
            ['Digital Signature:', certificate.digital_signature[:64] + '...' if len(certificate.digital_signature) > 64 else certificate.digital_signature],
        ]
        
        verification_table = Table(verification_data, colWidths=[120, 300])
        verification_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(verification_table)
        story.append(Spacer(1, 30))
        
        # Footer
        footer_text = f"""
        This certificate attests that the specified storage device has been securely wiped
        according to {certificate.nist_compliance} standards. The digital signature ensures
        the authenticity and integrity of this certificate.
        
        This certificate was generated by BitWipers - Secure Data Wiping System
        {certificate.organization}
        """
        
        footer = Paragraph(footer_text, normal_style)
        story.append(footer)
        
        # Build PDF
        doc.build(story)
    
    def export_public_key(self, output_path: str) -> bool:
        """
        Export public key for certificate verification.
        
        Args:
            output_path: Path to save public key
            
        Returns:
            bool: Success status
        """
        try:
            pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            with open(output_path, 'wb') as f:
                f.write(pem)
            
            return True
        except Exception:
            return False

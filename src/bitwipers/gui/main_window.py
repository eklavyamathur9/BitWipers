"""
Main GUI window for BitWipers.
Provides intuitive one-click interface for secure data wiping.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from typing import Optional, Dict, Any

from ..core.wiper import DataWiper, WipeResult, WipePattern, WipeStatus
from ..core.patterns import WipePatterns
from ..crypto.certificate import CertificateGenerator
from ..utils.device_detector import DeviceDetector
from ..utils.logger import Logger


class BitWipersGUI:
    """Main GUI application for BitWipers."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("BitWipers - Secure Data Wiping System")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize components
        self.device_detector = DeviceDetector()
        self.logger = Logger("BitWipersGUI")
        self.certificate_generator = CertificateGenerator()
        self.current_wiper: Optional[DataWiper] = None
        self.wipe_thread: Optional[threading.Thread] = None
        self.current_result: Optional[WipeResult] = None
        
        # GUI state
        self.selected_device = tk.StringVar()
        self.selected_pattern = tk.StringVar(value=WipePattern.NIST_CLEAR.value)
        self.verify_wipe = tk.BooleanVar(value=True)
        self.generate_certificate = tk.BooleanVar(value=True)
        self.quick_format = tk.BooleanVar(value=False)
        
        # Create GUI
        self._create_widgets()
        self._setup_layout()
        self._refresh_devices()
        
        # Configure styles
        self._configure_styles()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.title_label = ttk.Label(
            self.header_frame,
            text="BitWipers - Secure Data Wiping System",
            font=("Arial", 16, "bold")
        )
        self.subtitle_label = ttk.Label(
            self.header_frame,
            text="Trustworthy IT Asset Recycling • NIST SP 800-88 Compliant",
            font=("Arial", 10)
        )
        
        # Device selection frame
        self.device_frame = ttk.LabelFrame(self.main_frame, text="Device Selection", padding="10")
        self.device_label = ttk.Label(self.device_frame, text="Select Storage Device:")
        self.device_combo = ttk.Combobox(
            self.device_frame,
            textvariable=self.selected_device,
            width=50,
            state="readonly"
        )
        self.refresh_btn = ttk.Button(
            self.device_frame,
            text="Refresh",
            command=self._refresh_devices
        )
        self.browse_btn = ttk.Button(
            self.device_frame,
            text="Browse Files...",
            command=self._browse_files
        )
        
        # Device info frame
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Device Information", padding="10")
        self.info_text = tk.Text(
            self.info_frame,
            height=4,
            width=70,
            state="disabled",
            wrap=tk.WORD
        )
        
        # Wipe options frame
        self.options_frame = ttk.LabelFrame(self.main_frame, text="Wipe Options", padding="10")
        
        self.pattern_label = ttk.Label(self.options_frame, text="Wipe Pattern:")
        self.pattern_combo = ttk.Combobox(
            self.options_frame,
            textvariable=self.selected_pattern,
            values=[pattern.value for pattern in WipePattern],
            state="readonly",
            width=25
        )
        self.pattern_combo.bind("<<ComboboxSelected>>", self._on_pattern_selected)
        
        self.pattern_desc_label = ttk.Label(
            self.options_frame,
            text="",
            font=("Arial", 9),
            foreground="gray"
        )
        
        # Checkboxes
        self.verify_check = ttk.Checkbutton(
            self.options_frame,
            text="Verify wipe completion",
            variable=self.verify_wipe
        )
        self.cert_check = ttk.Checkbutton(
            self.options_frame,
            text="Generate tamper-proof certificate",
            variable=self.generate_certificate
        )
        self.format_check = ttk.Checkbutton(
            self.options_frame,
            text="Quick format after wipe",
            variable=self.quick_format
        )
        
        # Progress frame
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Progress", padding="10")
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(self.progress_frame, textvariable=self.progress_var)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=400,
            mode='determinate'
        )
        self.details_text = tk.Text(
            self.progress_frame,
            height=6,
            width=70,
            state="disabled",
            wrap=tk.WORD
        )
        
        # Control buttons frame
        self.control_frame = ttk.Frame(self.main_frame)
        self.wipe_btn = ttk.Button(
            self.control_frame,
            text="Start Secure Wipe",
            command=self._start_wipe,
            style="Accent.TButton"
        )
        self.cancel_btn = ttk.Button(
            self.control_frame,
            text="Cancel",
            command=self._cancel_wipe,
            state="disabled"
        )
        self.save_cert_btn = ttk.Button(
            self.control_frame,
            text="Save Certificate",
            command=self._save_certificate,
            state="disabled"
        )
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        )
    
    def _setup_layout(self):
        """Setup the layout of widgets."""
        # Main frame
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.title_label.grid(row=0, column=0, sticky="w")
        self.subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Device selection
        self.device_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.device_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.device_combo.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.refresh_btn.grid(row=1, column=1, padx=(5, 5))
        self.browse_btn.grid(row=1, column=2, padx=(5, 0))
        
        self.device_frame.grid_columnconfigure(0, weight=1)
        
        # Device info
        self.info_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.info_text.grid(row=0, column=0, sticky="ew")
        self.info_frame.grid_columnconfigure(0, weight=1)
        
        # Options
        self.options_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.pattern_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.pattern_combo.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 5))
        self.pattern_desc_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        self.verify_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        self.cert_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
        self.format_check.grid(row=4, column=0, columnspan=2, sticky="w", pady=2)
        
        # Progress
        self.progress_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.progress_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.details_text.grid(row=2, column=0, sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        self.control_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        self.wipe_btn.grid(row=0, column=0, padx=(0, 10))
        self.cancel_btn.grid(row=0, column=1, padx=(0, 10))
        self.save_cert_btn.grid(row=0, column=2)
        
        # Status bar
        self.status_frame.grid(row=6, column=0, columnspan=2, sticky="ew")
        self.status_label.grid(row=0, column=0, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # Configure main frame weight
        self.main_frame.grid_columnconfigure(1, weight=1)
    
    def _configure_styles(self):
        """Configure custom styles."""
        style = ttk.Style()
        
        # Configure accent button style
        style.configure(
            "Accent.TButton",
            font=("Arial", 10, "bold")
        )
    
    def _refresh_devices(self):
        """Refresh the list of available devices."""
        try:
            devices = self.device_detector.get_storage_devices()
            device_names = [f"{dev['name']} ({dev['path']})" for dev in devices]
            
            self.device_combo['values'] = device_names
            
            if device_names:
                self.device_combo.set(device_names[0])
                self._on_device_selected()
            else:
                self._update_info_text("No storage devices detected.")
                
            self.status_var.set(f"Found {len(devices)} storage device(s)")
            
        except Exception as e:
            self.logger.error(f"Error refreshing devices: {e}")
            messagebox.showerror("Error", f"Failed to refresh devices: {e}")
    
    def _browse_files(self):
        """Browse for files to wipe."""
        file_path = filedialog.askopenfilename(
            title="Select file to wipe",
            filetypes=[("All files", "*.*")]
        )
        
        if file_path:
            self.selected_device.set(f"File: {file_path}")
            self._update_info_text(f"Selected file: {file_path}\nSize: {self._format_bytes(os.path.getsize(file_path))}")
    
    def _on_device_selected(self, event=None):
        """Handle device selection change."""
        device_str = self.selected_device.get()
        if not device_str:
            return
        
        try:
            if device_str.startswith("File:"):
                # File selection
                file_path = device_str[6:]  # Remove "File: " prefix
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    info = f"File: {file_path}\nSize: {self._format_bytes(size)}"
                    self._update_info_text(info)
            else:
                # Device selection
                devices = self.device_detector.get_storage_devices()
                for device in devices:
                    if f"{device['name']} ({device['path']})" == device_str:
                        info = self._format_device_info(device)
                        self._update_info_text(info)
                        break
        except Exception as e:
            self.logger.error(f"Error getting device info: {e}")
    
    def _on_pattern_selected(self, event=None):
        """Handle wipe pattern selection change."""
        pattern_str = self.selected_pattern.get()
        try:
            pattern = WipePattern(pattern_str)
            description = WipePatterns.get_pattern_description(pattern)
            self.pattern_desc_label.config(text=description)
        except ValueError:
            self.pattern_desc_label.config(text="")
    
    def _start_wipe(self):
        """Start the wipe operation."""
        device_str = self.selected_device.get()
        if not device_str:
            messagebox.showerror("Error", "Please select a device or file to wipe.")
            return
        
        # Confirm operation
        if not self._confirm_wipe():
            return
        
        # Get device path
        if device_str.startswith("File:"):
            device_path = device_str[6:]
            wipe_type = "file"
        else:
            # Extract path from device string
            path_start = device_str.rfind("(") + 1
            path_end = device_str.rfind(")")
            device_path = device_str[path_start:path_end]
            wipe_type = "device"
        
        # Setup wiper
        self.current_wiper = DataWiper(
            progress_callback=self._progress_callback,
            verify_wipe=self.verify_wipe.get()
        )
        
        # Get pattern
        try:
            pattern = WipePattern(self.selected_pattern.get())
        except ValueError:
            pattern = WipePattern.NIST_CLEAR
        
        # Update UI state
        self._set_wiping_state(True)
        
        # Start wipe in separate thread
        def wipe_worker():
            try:
                if wipe_type == "file":
                    result = self.current_wiper.wipe_file(device_path, pattern)
                else:
                    result = self.current_wiper.wipe_device(
                        device_path, pattern, self.quick_format.get()
                    )
                
                # Update UI on main thread
                self.root.after(0, self._wipe_completed, result)
                
            except Exception as e:
                self.logger.error(f"Wipe error: {e}")
                self.root.after(0, self._wipe_error, str(e))
        
        self.wipe_thread = threading.Thread(target=wipe_worker)
        self.wipe_thread.start()
    
    def _cancel_wipe(self):
        """Cancel the current wipe operation."""
        if self.current_wiper:
            self.current_wiper.cancel_operation()
            self.status_var.set("Cancelling wipe operation...")
    
    def _confirm_wipe(self) -> bool:
        """Show confirmation dialog for wipe operation."""
        device_str = self.selected_device.get()
        pattern_str = self.selected_pattern.get()
        
        message = f"WARNING: This will permanently destroy all data!\n\n"
        message += f"Device/File: {device_str}\n"
        message += f"Wipe Pattern: {pattern_str}\n\n"
        message += "This operation cannot be undone. Are you sure?"
        
        return messagebox.askyesno(
            "Confirm Data Wipe",
            message,
            icon="warning"
        )
    
    def _progress_callback(self, result: WipeResult):
        """Handle progress updates from wiper."""
        self.root.after(0, self._update_progress, result)
    
    def _update_progress(self, result: WipeResult):
        """Update progress display."""
        self.current_result = result
        
        # Update progress bar
        progress = result.progress_percent
        self.progress_bar['value'] = progress
        
        # Update progress label
        if result.status == WipeStatus.IN_PROGRESS:
            self.progress_var.set(
                f"Pass {result.passes_completed}/{result.total_passes} - "
                f"{progress:.1f}% ({self._format_bytes(result.bytes_wiped)} / "
                f"{self._format_bytes(result.total_bytes)})"
            )
        else:
            self.progress_var.set(f"Status: {result.status.value.title()}")
        
        # Update details
        details = f"Pattern: {result.pattern.value}\n"
        details += f"Started: {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        if result.end_time:
            details += f"Duration: {result.duration:.2f} seconds\n"
        if result.error_message:
            details += f"Error: {result.error_message}\n"
        
        self._update_details_text(details)
        
        # Update status
        self.status_var.set(f"Wiping: {progress:.1f}% complete")
    
    def _wipe_completed(self, result: WipeResult):
        """Handle wipe completion."""
        self.current_result = result
        self._set_wiping_state(False)
        
        if result.status == WipeStatus.COMPLETED:
            self.status_var.set("Wipe completed successfully!")
            
            # Generate certificate if requested
            if self.generate_certificate.get():
                self._generate_certificate(result)
            
            messagebox.showinfo(
                "Wipe Complete",
                f"Data wipe completed successfully!\n\n"
                f"Duration: {result.duration:.2f} seconds\n"
                f"Bytes wiped: {self._format_bytes(result.bytes_wiped)}"
            )
        elif result.status == WipeStatus.CANCELLED:
            self.status_var.set("Wipe cancelled")
            messagebox.showwarning("Cancelled", "Wipe operation was cancelled.")
        else:
            self.status_var.set("Wipe failed")
            error_msg = result.error_message or "Unknown error occurred"
            messagebox.showerror("Wipe Failed", f"Wipe operation failed:\n{error_msg}")
    
    def _wipe_error(self, error_message: str):
        """Handle wipe errors."""
        self._set_wiping_state(False)
        self.status_var.set("Wipe failed")
        messagebox.showerror("Error", f"Wipe operation failed:\n{error_message}")
    
    def _generate_certificate(self, result: WipeResult):
        """Generate wipe certificate."""
        try:
            certificate = self.certificate_generator.generate_certificate(result)
            self.current_certificate = certificate
            self.save_cert_btn['state'] = 'normal'
            
            self.status_var.set("Certificate generated")
            
        except Exception as e:
            self.logger.error(f"Certificate generation error: {e}")
            messagebox.showerror(
                "Certificate Error",
                f"Failed to generate certificate: {e}"
            )
    
    def _save_certificate(self):
        """Save the wipe certificate."""
        if not hasattr(self, 'current_certificate'):
            messagebox.showerror("Error", "No certificate available to save.")
            return
        
        # Ask for save location and format
        file_path = filedialog.asksaveasfilename(
            title="Save Certificate",
            defaultextension=".pdf",
            filetypes=[
                ("PDF Certificate", "*.pdf"),
                ("JSON Certificate", "*.json")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.pdf'):
                    success = self.certificate_generator.save_certificate_pdf(
                        self.current_certificate, file_path
                    )
                else:
                    success = self.certificate_generator.save_certificate_json(
                        self.current_certificate, file_path
                    )
                
                if success:
                    messagebox.showinfo("Success", f"Certificate saved to:\n{file_path}")
                else:
                    messagebox.showerror("Error", "Failed to save certificate.")
                    
            except Exception as e:
                self.logger.error(f"Certificate save error: {e}")
                messagebox.showerror("Error", f"Failed to save certificate: {e}")
    
    def _set_wiping_state(self, wiping: bool):
        """Update UI state for wiping/not wiping."""
        if wiping:
            self.wipe_btn['state'] = 'disabled'
            self.cancel_btn['state'] = 'normal'
            self.device_combo['state'] = 'disabled'
            self.pattern_combo['state'] = 'disabled'
        else:
            self.wipe_btn['state'] = 'normal'
            self.cancel_btn['state'] = 'disabled'
            self.device_combo['state'] = 'readonly'
            self.pattern_combo['state'] = 'readonly'
    
    def _update_info_text(self, text: str):
        """Update the info text widget."""
        self.info_text['state'] = 'normal'
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        self.info_text['state'] = 'disabled'
    
    def _update_details_text(self, text: str):
        """Update the details text widget."""
        self.details_text['state'] = 'normal'
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, text)
        self.details_text['state'] = 'disabled'
    
    def _format_device_info(self, device: Dict[str, Any]) -> str:
        """Format device information for display."""
        info = f"Name: {device['name']}\n"
        info += f"Path: {device['path']}\n"
        if 'size' in device:
            info += f"Size: {self._format_bytes(device['size'])}\n"
        if 'type' in device:
            info += f"Type: {device['type']}\n"
        return info
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format byte count for human readability."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
    
    def run(self):
        """Run the GUI application."""
        # Initialize pattern description
        self._on_pattern_selected()
        
        # Start the main loop
        self.root.mainloop()


def main():
    """Main entry point for GUI application."""
    app = BitWipersGUI()
    app.run()


if __name__ == "__main__":
    main()

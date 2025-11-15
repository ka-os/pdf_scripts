#!/usr/bin/env python3
"""
PDF Metadata Extractor
Displays metadata information from PDF files.
"""

import sys
import os
from datetime import datetime

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf library not found.")
    print("Please install it using: pip install pypdf")
    sys.exit(1)


def format_pdf_date(pdf_date):
    """Convert PDF date format (D:YYYYMMDDHHmmSS) to readable format."""
    if not pdf_date or not isinstance(pdf_date, str):
        return pdf_date
    
    # Remove 'D:' prefix if present
    if pdf_date.startswith('D:'):
        pdf_date = pdf_date[2:]
    
    try:
        # Parse the date (format: YYYYMMDDHHmmSS)
        date_part = pdf_date[:14]  # Take first 14 characters
        dt = datetime.strptime(date_part, '%Y%m%d%H%M%S')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, IndexError):
        return pdf_date


def display_metadata(pdf_path):
    """Extract and display metadata from a PDF file."""
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        return False
    
    # Check if file is readable
    if not os.path.isfile(pdf_path):
        print(f"Error: '{pdf_path}' is not a file.")
        return False
    
    try:
        # Open PDF file
        reader = PdfReader(pdf_path)
        
        print(f"\n{'='*60}")
        print(f"PDF Metadata for: {pdf_path}")
        print(f"{'='*60}\n")
        
        # Basic file information
        print(f"File Size: {os.path.getsize(pdf_path):,} bytes")
        print(f"Number of Pages: {len(reader.pages)}")
        print(f"PDF Version: {reader.pdf_header if hasattr(reader, 'pdf_header') else 'Unknown'}")
        
        # Check if encrypted
        if reader.is_encrypted:
            print(f"Encrypted: Yes")
        else:
            print(f"Encrypted: No")
        
        print(f"\n{'Metadata Information':-^60}\n")
        
        # Extract metadata
        metadata = reader.metadata
        
        if metadata:
            # Standard metadata fields
            metadata_fields = {
                '/Title': 'Title',
                '/Author': 'Author',
                '/Subject': 'Subject',
                '/Creator': 'Creator',
                '/Producer': 'Producer',
                '/CreationDate': 'Creation Date',
                '/ModDate': 'Modification Date',
                '/Keywords': 'Keywords',
                '/Trapped': 'Trapped'
            }
            
            found_metadata = False
            for key, label in metadata_fields.items():
                if key in metadata and metadata[key]:
                    value = metadata[key]
                    
                    # Format dates
                    if 'Date' in label:
                        value = format_pdf_date(value)
                    
                    print(f"{label:20}: {value}")
                    found_metadata = True
            
            # Display any additional custom metadata
            custom_fields = [k for k in metadata.keys() if k not in metadata_fields]
            if custom_fields:
                print(f"\n{'Custom Metadata':-^60}\n")
                for key in custom_fields:
                    print(f"{key:20}: {metadata[key]}")
                found_metadata = True
            
            if not found_metadata:
                print("No metadata found in this PDF file.")
        else:
            print("No metadata found in this PDF file.")
        
        print(f"\n{'='*60}\n")
        return True
        
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return False


def print_usage():
    """Print script usage information."""
    script_name = os.path.basename(sys.argv[0])
    print(f"\nUsage: python {script_name} <pdf_file>")
    print(f"   or: {script_name} <pdf_file>")
    print("\nDescription:")
    print("  Extracts and displays metadata from a PDF file.")
    print("\nArguments:")
    print("  <pdf_file>    Path to the PDF file to extract metadata from")
    print("\nExample:")
    print(f"  python {script_name} document.pdf")
    print(f"  python {script_name} /path/to/file.pdf\n")


def main():
    """Main function to handle command-line arguments."""
    
    if len(sys.argv) < 2:
        print("\nError: No PDF file specified.")
        print_usage()
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    # Display help if requested
    if pdf_file in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    # Process the PDF file
    success = display_metadata(pdf_file)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

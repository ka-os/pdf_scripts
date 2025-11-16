#!/usr/bin/env python3
"""
PDF Page Splitter
Splits a PDF file into individual pages.
"""

import sys
import os

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: pypdf library not found.")
    print("Install it using: pip install pypdf")
    sys.exit(1)


def split_pdf(input_file):
    """Split PDF into individual page files."""
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return False
    
    if not input_file.lower().endswith('.pdf'):
        print(f"Error: '{input_file}' is not a PDF file.")
        return False
    
    try:
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        
        if total_pages == 0:
            print("Error: PDF file has no pages.")
            return False
        
        # Get base filename without extension
        base_name = os.path.splitext(input_file)[0]
        
        print(f"Splitting '{input_file}' ({total_pages} pages)...\n")
        
        for page_num in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            
            # Format page number with leading zero for single digits
            page_str = f"{page_num + 1:02d}"
            output_file = f"{base_name}_page_{page_str}.pdf"
            
            with open(output_file, 'wb') as output:
                writer.write(output)
            
            print(f"Created: {output_file}")
        
        print(f"\nSuccessfully split {total_pages} pages.")
        return True
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


def print_usage():
    """Print usage information."""
    script_name = os.path.basename(sys.argv[0])
    print(f"\nUsage: python {script_name} <pdf_file>")
    print("\nDescription:")
    print("  Splits a PDF file into individual page files.")
    print("\nArguments:")
    print("  <pdf_file>    Path to the PDF file to split")
    print("\nExample:")
    print(f"  python {script_name} sample_file.pdf")
    print("\nOutput:")
    print("  Creates files named: sample_file_page_01.pdf, sample_file_page_02.pdf, etc.\n")


def main():
    """Main function."""
    
    if len(sys.argv) < 2:
        print("\nError: No PDF file specified.")
        print_usage()
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if pdf_file in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    success = split_pdf(pdf_file)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

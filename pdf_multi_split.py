#!/usr/bin/env python3
"""
PDF Multi-Point Splitter
Splits a PDF file at specified page numbers.
"""

import sys
import os

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: pypdf library not found.")
    print("Install it using: pip install pypdf")
    sys.exit(1)


def parse_split_points(split_arg):
    """Parse split points from argument (e.g., '7' or '7,11')."""
    try:
        points = [int(p.strip()) for p in split_arg.split(',')]
        return sorted(points)
    except ValueError:
        print(f"Error: Invalid split point format '{split_arg}'.")
        print("Use comma-separated numbers, e.g., '7' or '7,11'")
        return None


def split_pdf_multi(input_file, split_points):
    """Split PDF at multiple points."""
    
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
        
        # Validate split points
        for point in split_points:
            if point < 1 or point >= total_pages:
                print(f"Error: Split point {point} is out of range (1-{total_pages-1}).")
                return False
        
        # Get base filename without extension
        base_name = os.path.splitext(input_file)[0]
        
        # Create ranges for splitting
        ranges = []
        start = 0
        for point in split_points:
            ranges.append((start, point - 1))  # point-1 because we want pages up to the split point
            start = point
        ranges.append((start, total_pages - 1))  # Last segment
        
        print(f"Splitting '{input_file}' ({total_pages} pages) at points: {split_points}\n")
        
        # Create each split file
        for idx, (start_page, end_page) in enumerate(ranges):
            writer = PdfWriter()
            
            # Add pages from start to end (inclusive)
            for page_num in range(start_page, end_page + 1):
                writer.add_page(reader.pages[page_num])
            
            # Format page numbers with leading zeros
            start_str = f"{start_page + 1:02d}"
            end_str = f"{end_page + 1:02d}"
            output_file = f"{base_name}_pages_{start_str}_{end_str}.pdf"
            
            with open(output_file, 'wb') as output:
                writer.write(output)
            
            print(f"Created: {output_file} (pages {start_page + 1}-{end_page + 1})")
        
        print(f"\nSuccessfully created {len(ranges)} files.")
        return True
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


def print_usage():
    """Print usage information."""
    script_name = os.path.basename(sys.argv[0])
    print(f"\nUsage: python {script_name} <pdf_file> <split_points>")
    print("\nDescription:")
    print("  Splits a PDF file at specified page numbers.")
    print("\nArguments:")
    print("  <pdf_file>       Path to the PDF file to split")
    print("  <split_points>   Page number(s) where splits occur (comma-separated)")
    print("\nExamples:")
    print(f"  python {script_name} sample_file.pdf 7")
    print(f"    → Creates: sample_file_pages_01_07.pdf, sample_file_pages_08_15.pdf")
    print(f"\n  python {script_name} sample_file.pdf 7,11")
    print(f"    → Creates: sample_file_pages_01_07.pdf, sample_file_pages_08_11.pdf,")
    print(f"               sample_file_pages_12_15.pdf\n")


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
    
    if len(sys.argv) < 3:
        print("\nError: No split points specified.")
        print_usage()
        sys.exit(1)
    
    split_arg = sys.argv[2]
    split_points = parse_split_points(split_arg)
    
    if split_points is None:
        sys.exit(1)
    
    success = split_pdf_multi(pdf_file, split_points)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

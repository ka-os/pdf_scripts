#!/usr/bin/env python3
"""
PDF Merger
Merges multiple PDF files into a single file.
"""

import sys
import os

try:
    from pypdf import PdfWriter, PdfReader
except ImportError:
    print("Error: pypdf library not found.")
    print("Install it using: pip install pypdf")
    sys.exit(1)


def parse_arguments():
    """Parse command-line arguments."""
    args = sys.argv[1:]
    
    if '-h' in args or '--help' in args or 'help' in args:
        return None, None, True
    
    output_file = None
    source_files = []
    
    # Find -o argument
    if '-o' in args:
        o_index = args.index('-o')
        if o_index + 1 < len(args):
            output_file = args[o_index + 1]
            if not output_file.endswith('.pdf'):
                output_file += '.pdf'
        else:
            print("Error: No output filename specified after -o.")
            return None, None, False
    else:
        print("Error: Missing required argument -o (output filename).")
        return None, None, False
    
    # Find -s argument
    if '-s' in args:
        s_index = args.index('-s')
        # Get all files after -s
        source_files = [arg for arg in args[s_index + 1:] if not arg.startswith('-')]
        
        if not source_files:
            print("Error: No source files specified after -s.")
            return None, None, False
    else:
        print("Error: Missing required argument -s (source files).")
        return None, None, False
    
    return output_file, source_files, False


def merge_pdfs(output_file, source_files):
    """Merge multiple PDF files into one."""
    
    # Validate all source files exist
    for pdf_file in source_files:
        if not os.path.exists(pdf_file):
            print(f"Error: File '{pdf_file}' not found.")
            return False
        if not pdf_file.lower().endswith('.pdf'):
            print(f"Error: '{pdf_file}' is not a PDF file.")
            return False
    
    try:
        writer = PdfWriter()
        
        print(f"Merging {len(source_files)} PDF file(s)...\n")
        
        for pdf_file in source_files:
            print(f"Adding: {pdf_file}")
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
        
        # Write merged PDF
        with open(output_file, 'wb') as output:
            writer.write(output)
        
        print(f"\nSuccessfully created: {output_file}")
        print(f"Total pages: {len(writer.pages)}")
        return True
        
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False


def print_usage():
    """Print usage information."""
    script_name = os.path.basename(sys.argv[0])
    print(f"\nUsage: python {script_name} -o <output_file> -s <source_file1> [source_file2] ...")
    print("\nDescription:")
    print("  Merges multiple PDF files into a single file.")
    print("\nArguments:")
    print("  -o <output_file>  Output filename (required)")
    print("  -s <source_files> Source PDF files to merge (required, one or more)")
    print("\nExamples:")
    print(f"  python {script_name} -o merged.pdf -s file1.pdf file2.pdf")
    print(f"  python {script_name} -o new_file -s sample1.pdf sample2.pdf sample3.pdf")
    print(f"    → Creates: new_file.pdf\n")


def main():
    """Main function."""
    
    if len(sys.argv) < 2:
        print("\nError: No arguments provided.")
        print_usage()
        sys.exit(1)
    
    output_file, source_files, show_help = parse_arguments()
    
    if show_help:
        print_usage()
        sys.exit(0)
    
    if output_file is None or source_files is None:
        print_usage()
        sys.exit(1)
    
    success = merge_pdfs(output_file, source_files)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

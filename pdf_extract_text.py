#!/usr/bin/env python3
"""
PDF Text Extractor
Extracts text and table content from PDF files to TXT format.
"""

import sys
import os

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber library not found.")
    print("Install it using: pip install pdfplumber")
    sys.exit(1)


def extract_text_and_tables(pdf_file):
    """Extract text and tables from PDF file."""
    if not os.path.exists(pdf_file):
        print(f"Error: File '{pdf_file}' not found.")
        return None
    
    if not pdf_file.lower().endswith('.pdf'):
        print(f"Error: '{pdf_file}' is not a PDF file.")
        return None
    
    try:
        content = []
        
        with pdfplumber.open(pdf_file) as pdf:
            print(f"Processing {len(pdf.pages)} page(s)...")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"  Extracting page {page_num}...")
                
                # Add page header
                content.append(f"{'='*70}")
                content.append(f"PAGE {page_num}")
                content.append(f"{'='*70}")
                content.append("")
                
                # Extract text
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        content.append(text)
                        content.append("")
                except Exception as e:
                    content.append(f"[Error extracting text: {str(e)[:50]}]")
                    content.append("")
                
                # Extract tables
                try:
                    tables = page.extract_tables()
                    if tables:
                        for table_num, table in enumerate(tables, 1):
                            content.append(f"{'-'*70}")
                            content.append(f"TABLE {table_num} (Page {page_num})")
                            content.append(f"{'-'*70}")
                            
                            if table:
                                # Calculate column widths
                                col_widths = []
                                for col_idx in range(len(table[0]) if table else 0):
                                    max_width = max(
                                        len(str(row[col_idx] or '')) 
                                        for row in table if col_idx < len(row)
                                    )
                                    col_widths.append(max(max_width, 5))  # Minimum width of 5
                                
                                # Format table rows
                                for row in table:
                                    formatted_row = []
                                    for col_idx, cell in enumerate(row):
                                        cell_str = str(cell or '')
                                        if col_idx < len(col_widths):
                                            formatted_row.append(cell_str.ljust(col_widths[col_idx]))
                                    content.append(' | '.join(formatted_row))
                                
                                content.append("")
                except Exception as e:
                    content.append(f"[Error extracting tables: {str(e)[:50]}]")
                    content.append("")
        
        return '\n'.join(content)
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None


def save_text(content, source_file):
    """Save extracted text to file."""
    base_name = os.path.splitext(source_file)[0]
    output_file = f"{base_name}.txt"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nText extracted successfully!")
        print(f"Output saved to: {output_file}")
        return True
    except Exception as e:
        print(f"Error saving output: {e}")
        return False


def print_usage():
    """Print usage information."""
    script_name = os.path.basename(sys.argv[0])
    print(f"\nUsage: python {script_name} <pdf_file>")
    print("\nDescription:")
    print("  Extracts text and table content from PDF files to TXT format.")
    print("  Uses document layout analysis for accurate extraction.")
    print("\nArguments:")
    print("  <pdf_file>     Source PDF file (mandatory)")
    print("\nOutput:")
    print("  Creates a .txt file with the same name as the source PDF")
    print("\nExamples:")
    print(f"  python {script_name} sample_file.pdf")
    print(f"    → Creates: sample_file.txt")
    print(f"\n  python {script_name} document.pdf")
    print(f"    → Creates: document.txt\n")


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
    
    # Extract text and tables
    content = extract_text_and_tables(pdf_file)
    
    if content is None:
        sys.exit(1)
    
    if not content.strip():
        print("\nWarning: No text or tables found in PDF.")
        print("Creating empty output file.")
    
    # Save output
    success = save_text(content, pdf_file)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

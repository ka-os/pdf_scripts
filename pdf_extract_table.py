#!/usr/bin/env python3
"""
PDF Table Extractor
Extracts tables from PDF files and outputs to TXT or HTML format.
"""

import sys
import os

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber library not found.")
    print("Install it using: pip install pdfplumber")
    sys.exit(1)


def parse_arguments():
    """Parse command-line arguments."""
    args = sys.argv[1:]
    
    if '-h' in args and len(args) == 1:
        return None, None, True
    if '--help' in args or 'help' in args:
        return None, None, True
    
    output_type = None
    source_file = None
    
    # Find output type
    if '-t' in args or '-txt' in args:
        output_type = 'txt'
        type_arg = '-t' if '-t' in args else '-txt'
        type_index = args.index(type_arg)
        # Get source file (next argument after type)
        if type_index + 1 < len(args):
            source_file = args[type_index + 1]
    elif '-h' in args or '-html' in args:
        output_type = 'html'
        type_arg = '-h' if '-h' in args else '-html'
        type_index = args.index(type_arg)
        # Get source file (next argument after type)
        if type_index + 1 < len(args):
            source_file = args[type_index + 1]
    else:
        print("Error: Missing output type argument (-t/-txt or -h/-html).")
        return None, None, False
    
    if not source_file:
        print("Error: Missing source PDF file argument.")
        return None, None, False
    
    return output_type, source_file, False


def extract_tables(pdf_file):
    """Extract all tables from PDF file."""
    if not os.path.exists(pdf_file):
        print(f"Error: File '{pdf_file}' not found.")
        return None
    
    if not pdf_file.lower().endswith('.pdf'):
        print(f"Error: '{pdf_file}' is not a PDF file.")
        return None
    
    try:
        all_tables = []
        with pdfplumber.open(pdf_file) as pdf:
            print(f"Processing {len(pdf.pages)} page(s)...")
            
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                if tables:
                    print(f"Found {len(tables)} table(s) on page {page_num}")
                    for table in tables:
                        all_tables.append({
                            'page': page_num,
                            'data': table
                        })
        
        if not all_tables:
            print("No tables found in PDF.")
            return []
        
        print(f"Total tables extracted: {len(all_tables)}")
        return all_tables
        
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return None


def tables_to_txt(tables):
    """Convert tables to plain text format."""
    output = []
    
    for idx, table_info in enumerate(tables, 1):
        output.append(f"{'='*80}")
        output.append(f"Table {idx} (Page {table_info['page']})")
        output.append(f"{'='*80}")
        output.append("")
        
        table = table_info['data']
        if not table:
            continue
        
        # Calculate column widths
        col_widths = []
        for col_idx in range(len(table[0]) if table else 0):
            max_width = max(
                len(str(row[col_idx] or '')) 
                for row in table if col_idx < len(row)
            )
            col_widths.append(max_width)
        
        # Format rows
        for row in table:
            formatted_row = []
            for col_idx, cell in enumerate(row):
                cell_str = str(cell or '')
                if col_idx < len(col_widths):
                    formatted_row.append(cell_str.ljust(col_widths[col_idx]))
            output.append(' | '.join(formatted_row))
        
        output.append("")
    
    return '\n'.join(output)


def tables_to_html(tables):
    """Convert tables to HTML format."""
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<title>Extracted Tables</title>")
    html.append("<style>")
    html.append("body { font-family: Arial, sans-serif; margin: 20px; }")
    html.append("h2 { color: #333; }")
    html.append("table { border-collapse: collapse; margin: 20px 0; width: 100%; }")
    html.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
    html.append("th { background-color: #4CAF50; color: white; }")
    html.append("tr:nth-child(even) { background-color: #f2f2f2; }")
    html.append("</style>")
    html.append("</head>")
    html.append("<body>")
    html.append("<h1>Extracted Tables</h1>")
    
    for idx, table_info in enumerate(tables, 1):
        html.append(f"<h2>Table {idx} (Page {table_info['page']})</h2>")
        html.append("<table>")
        
        table = table_info['data']
        if not table:
            continue
        
        # First row as header
        if table:
            html.append("<thead><tr>")
            for cell in table[0]:
                html.append(f"<th>{cell or ''}</th>")
            html.append("</tr></thead>")
        
        # Remaining rows as body
        if len(table) > 1:
            html.append("<tbody>")
            for row in table[1:]:
                html.append("<tr>")
                for cell in row:
                    html.append(f"<td>{cell or ''}</td>")
                html.append("</tr>")
            html.append("</tbody>")
        
        html.append("</table>")
    
    html.append("</body>")
    html.append("</html>")
    
    return '\n'.join(html)


def save_output(content, source_file, output_type):
    """Save extracted tables to file."""
    base_name = os.path.splitext(source_file)[0]
    extension = 'txt' if output_type == 'txt' else 'html'
    output_file = f"{base_name}_tables.{extension}"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nOutput saved to: {output_file}")
        return True
    except Exception as e:
        print(f"Error saving output: {e}")
        return False


def print_usage():
    """Print usage information."""
    script_name = os.path.basename(sys.argv[0])
    print(f"\nUsage: python {script_name} <-t|-txt|-h|-html> <pdf_file>")
    print("\nDescription:")
    print("  Extracts tables from PDF files and outputs to TXT or HTML format.")
    print("\nArguments:")
    print("  -t, -txt       Output in plain text format (mandatory)")
    print("  -h, -html      Output in HTML format (mandatory)")
    print("  <pdf_file>     Source PDF file (mandatory)")
    print("\nExamples:")
    print(f"  python {script_name} -t sample_file.pdf")
    print(f"  python {script_name} -txt sample_file.pdf")
    print(f"  python {script_name} -h sample_file.pdf")
    print(f"  python {script_name} -html sample_file.pdf\n")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("\nError: No arguments provided.")
        print_usage()
        sys.exit(1)
    
    output_type, source_file, show_help = parse_arguments()
    
    if show_help:
        print_usage()
        sys.exit(0)
    
    if output_type is None or source_file is None:
        print_usage()
        sys.exit(1)
    
    # Extract tables
    tables = extract_tables(source_file)
    
    if tables is None:
        sys.exit(1)
    
    if not tables:
        print("No output file created (no tables found).")
        sys.exit(0)
    
    # Convert to requested format
    if output_type == 'txt':
        content = tables_to_txt(tables)
    else:
        content = tables_to_html(tables)
    
    # Save output
    success = save_output(content, source_file, output_type)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

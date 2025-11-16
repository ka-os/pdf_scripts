#!/usr/bin/env python3
"""
PDF Internals Analyzer
Extracts and displays information about internal elements and objects in PDF files.
Uses multiple methods for robust font extraction.
"""

import sys
import os
import re
from collections import defaultdict

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber library not found.")
    print("Install it using: pip install pdfplumber")
    sys.exit(1)

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf library not found.")
    print("Install it using: pip install pypdf")
    sys.exit(1)

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


def analyze_fonts_pymupdf(pdf_file):
    """Extract fonts using PyMuPDF - most reliable method."""
    if not PYMUPDF_AVAILABLE:
        return {}, ["PyMuPDF not installed"], False
    
    fonts = defaultdict(list)
    errors = []
    
    try:
        doc = fitz.open(pdf_file)
        
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                font_list = page.get_fonts(full=True)
                
                for font in font_list:
                    # font structure: (xref, ext, type, basefont, name, encoding, embedded)
                    try:
                        xref, ext, font_type, basefont, name, encoding = font[:6]
                        embedded = font[6] if len(font) > 6 else False
                        
                        font_info = f"{basefont} ({font_type})"
                        if encoding and encoding != "":
                            font_info += f" - {encoding}"
                        if embedded:
                            font_info += " [Embedded]"
                        
                        if (page_num + 1) not in fonts[font_info]:
                            fonts[font_info].append(page_num + 1)
                    except Exception as e:
                        errors.append(f"Page {page_num + 1}, font parsing: {str(e)[:50]}")
                        
            except Exception as e:
                errors.append(f"Page {page_num + 1}: {str(e)[:50]}")
        
        doc.close()
        return fonts, errors, True
        
    except Exception as e:
        errors.append(f"General error: {str(e)[:50]}")
        return fonts, errors, False


def analyze_fonts_robust(reader):
    """Analyze fonts using direct dictionary access."""
    fonts = defaultdict(list)
    errors = []
    
    try:
        for page_num, page in enumerate(reader.pages, 1):
            try:
                # Access page dictionary directly
                page_obj = page.get_object() if hasattr(page, 'get_object') else page
                
                # Try multiple paths to resources
                resources = None
                if '/Resources' in page_obj:
                    resources = page_obj['/Resources']
                elif hasattr(page, 'get') and page.get('/Resources'):
                    resources = page.get('/Resources')
                
                if resources:
                    # Get Font dictionary
                    font_dict = None
                    if '/Font' in resources:
                        font_dict = resources['/Font']
                    
                    if font_dict:
                        # Iterate through fonts
                        for font_key in font_dict:
                            try:
                                font_ref = font_dict[font_key]
                                font_obj = font_ref.get_object() if hasattr(font_ref, 'get_object') else font_ref
                                
                                # Extract font properties
                                base_font = font_obj.get('/BaseFont', 'Unknown')
                                subtype = font_obj.get('/Subtype', 'Unknown')
                                encoding = font_obj.get('/Encoding', None)
                                
                                # Get font descriptor for more details
                                descriptor = None
                                if '/FontDescriptor' in font_obj:
                                    desc_ref = font_obj['/FontDescriptor']
                                    descriptor = desc_ref.get_object() if hasattr(desc_ref, 'get_object') else desc_ref
                                
                                font_info_str = f"{str(base_font).replace('/', '')} ({str(subtype).replace('/', '')})"
                                
                                if encoding and encoding not in ['Unknown', None]:
                                    font_info_str += f" - {str(encoding).replace('/', '')}"
                                
                                if descriptor:
                                    font_name = descriptor.get('/FontName', None)
                                    if font_name and font_name != base_font:
                                        font_info_str += f" [{str(font_name).replace('/', '')}]"
                                
                                if page_num not in fonts[font_info_str]:
                                    fonts[font_info_str].append(page_num)
                                    
                            except Exception as e:
                                errors.append(f"Page {page_num}, font '{font_key}': {str(e)[:50]}")
                                
            except Exception as e:
                errors.append(f"Page {page_num}: {str(e)[:50]}")
    except Exception as e:
        errors.append(f"General error: {str(e)[:50]}")
    
    return fonts, errors


def extract_fonts_from_content_stream(reader):
    """Extract font usage by parsing content streams."""
    fonts = defaultdict(list)
    errors = []
    
    for page_num, page in enumerate(reader.pages, 1):
        try:
            # Get page object
            page_obj = page.get_object() if hasattr(page, 'get_object') else page
            
            # Get contents
            if '/Contents' in page_obj:
                contents = page_obj['/Contents']
                
                # Handle array of content streams
                if isinstance(contents, list):
                    content_streams = contents
                else:
                    content_streams = [contents]
                
                # Get resources
                resources = page_obj.get('/Resources', {})
                font_dict = resources.get('/Font', {}) if resources else {}
                
                for content_ref in content_streams:
                    try:
                        content_obj = content_ref.get_object() if hasattr(content_ref, 'get_object') else content_ref
                        
                        if hasattr(content_obj, 'get_data'):
                            data = content_obj.get_data()
                        elif isinstance(content_obj, bytes):
                            data = content_obj
                        else:
                            continue
                        
                        # Decode if needed
                        try:
                            text = data.decode('latin-1', errors='ignore')
                        except:
                            text = str(data)
                        
                        # Find font references (Tf operator)
                        # Pattern: /F1 12 Tf or /Font1 10 Tf
                        font_refs = re.findall(r'/(\w+)\s+[\d.]+\s+Tf', text)
                        
                        for font_ref in font_refs:
                            font_key = f'/{font_ref}'
                            if font_key in font_dict:
                                font_obj = font_dict[font_key]
                                if hasattr(font_obj, 'get_object'):
                                    font_obj = font_obj.get_object()
                                
                                base_font = font_obj.get('/BaseFont', 'Unknown')
                                subtype = font_obj.get('/Subtype', 'Unknown')
                                
                                font_name = f"{str(base_font).replace('/', '')} ({str(subtype).replace('/', '')})"
                                if page_num not in fonts[font_name]:
                                    fonts[font_name].append(page_num)
                                    
                    except Exception as e:
                        errors.append(f"Page {page_num}, content stream: {str(e)[:50]}")
                        
        except Exception as e:
            errors.append(f"Page {page_num}: {str(e)[:50]}")
    
    return fonts, errors


def analyze_fonts_multi_method(reader, pdf_file):
    """Try multiple methods to extract font information."""
    
    # Method 1: Try PyMuPDF first (most reliable)
    if PYMUPDF_AVAILABLE:
        fonts, errors, success = analyze_fonts_pymupdf(pdf_file)
        if success and fonts:
            return fonts, errors, "PyMuPDF"
    
    # Method 2: Direct dictionary access
    fonts, errors = analyze_fonts_robust(reader)
    if fonts:
        return fonts, errors, "Direct Dictionary Access"
    
    # Method 3: Content stream parsing
    fonts, errors = extract_fonts_from_content_stream(reader)
    if fonts:
        return fonts, errors, "Content Stream Parsing"
    
    # If all methods found nothing, return the errors from PyMuPDF or direct access
    if PYMUPDF_AVAILABLE:
        fonts, errors, _ = analyze_fonts_pymupdf(pdf_file)
        return fonts, errors, "PyMuPDF (no fonts found)"
    else:
        fonts, errors = analyze_fonts_robust(reader)
        return fonts, errors, "Direct Access (no fonts found)"


def analyze_images(pdf):
    """Analyze images in the PDF."""
    images = defaultdict(list)
    errors = []
    
    try:
        for page_num, page in enumerate(pdf.pages, 1):
            try:
                page_images = page.images
                if page_images:
                    for img in page_images:
                        try:
                            width = int(img.get('width', 0))
                            height = int(img.get('height', 0))
                            img_key = f"{width}x{height}px"
                            if page_num not in images[img_key]:
                                images[img_key].append(page_num)
                        except Exception as e:
                            errors.append(f"Page {page_num}, image: {str(e)[:50]}")
            except Exception as e:
                errors.append(f"Page {page_num}: {str(e)[:50]}")
    except Exception as e:
        errors.append(f"General error: {str(e)[:50]}")
    
    return images, errors


def analyze_tables(pdf):
    """Analyze tables in the PDF."""
    tables = defaultdict(list)
    errors = []
    
    try:
        for page_num, page in enumerate(pdf.pages, 1):
            try:
                page_tables = page.extract_tables()
                if page_tables:
                    for idx, table in enumerate(page_tables, 1):
                        try:
                            if table:
                                rows = len(table)
                                cols = len(table[0]) if table else 0
                                table_key = f"{rows}x{cols} cells"
                                tables[table_key].append(page_num)
                        except Exception as e:
                            errors.append(f"Page {page_num}, table {idx}: {str(e)[:50]}")
            except Exception as e:
                errors.append(f"Page {page_num}: {str(e)[:50]}")
    except Exception as e:
        errors.append(f"General error: {str(e)[:50]}")
    
    return tables, errors


def analyze_text(pdf):
    """Analyze text content in the PDF."""
    text_info = {}
    total_chars = 0
    pages_with_text = []
    errors = []
    
    try:
        for page_num, page in enumerate(pdf.pages, 1):
            try:
                text = page.extract_text()
                if text and text.strip():
                    char_count = len(text)
                    total_chars += char_count
                    pages_with_text.append(page_num)
            except Exception as e:
                errors.append(f"Page {page_num}: {str(e)[:50]}")
    except Exception as e:
        errors.append(f"General error: {str(e)[:50]}")
    
    text_info['total_characters'] = total_chars
    text_info['pages_with_text'] = pages_with_text
    
    return text_info, errors


def analyze_annotations(reader):
    """Analyze annotations in the PDF."""
    annotations = defaultdict(list)
    errors = []
    
    try:
        for page_num, page in enumerate(reader.pages, 1):
            try:
                if '/Annots' in page:
                    annots = page['/Annots']
                    if annots:
                        try:
                            annot_list = annots.get_object() if hasattr(annots, 'get_object') else annots
                            for annot in annot_list:
                                try:
                                    annot_obj = annot.get_object()
                                    annot_type = annot_obj.get('/Subtype', 'Unknown')
                                    annot_key = str(annot_type).replace('/', '')
                                    if page_num not in annotations[annot_key]:
                                        annotations[annot_key].append(page_num)
                                except Exception as e:
                                    errors.append(f"Page {page_num}, annotation: {str(e)[:50]}")
                        except Exception as e:
                            errors.append(f"Page {page_num}: {str(e)[:50]}")
            except Exception as e:
                errors.append(f"Page {page_num}: {str(e)[:50]}")
    except Exception as e:
        errors.append(f"General error: {str(e)[:50]}")
    
    return annotations, errors


def analyze_forms(reader):
    """Analyze form fields in the PDF."""
    forms = defaultdict(list)
    errors = []
    
    try:
        if '/Root' in reader.trailer and '/AcroForm' in reader.trailer['/Root']:
            try:
                acro_form = reader.trailer['/Root']['/AcroForm']
                if acro_form and '/Fields' in acro_form:
                    fields = acro_form['/Fields']
                    if fields:
                        for field in fields:
                            try:
                                field_obj = field.get_object()
                                field_type = field_obj.get('/FT', 'Unknown')
                                field_name = field_obj.get('/T', 'Unnamed')
                                
                                # Try to find which page the field is on
                                if '/P' in field_obj:
                                    page_ref = field_obj['/P']
                                    for page_num, page in enumerate(reader.pages, 1):
                                        if page.indirect_reference == page_ref:
                                            forms[str(field_type)].append(page_num)
                                            break
                            except Exception as e:
                                errors.append(f"Form field: {str(e)[:50]}")
            except Exception as e:
                errors.append(f"AcroForm: {str(e)[:50]}")
    except Exception as e:
        errors.append(f"General error: {str(e)[:50]}")
    
    return forms, errors


def analyze_compression(reader):
    """Analyze compression methods used."""
    compression = defaultdict(int)
    errors = []
    
    try:
        for obj_num in range(len(reader.xref)):
            try:
                obj = reader.get_object(obj_num)
                if hasattr(obj, 'get') and '/Filter' in obj:
                    filter_val = obj['/Filter']
                    if isinstance(filter_val, list):
                        for f in filter_val:
                            compression[str(f)] += 1
                    else:
                        compression[str(filter_val)] += 1
            except Exception as e:
                # Skip objects that can't be read
                pass
    except Exception as e:
        errors.append(f"General error: {str(e)[:50]}")
    
    return compression, errors


def analyze_pdf(pdf_file):
    """Main analysis function."""
    if not os.path.exists(pdf_file):
        print(f"Error: File '{pdf_file}' not found.")
        return False
    
    if not pdf_file.lower().endswith('.pdf'):
        print(f"Error: '{pdf_file}' is not a PDF file.")
        return False
    
    try:
        print(f"\n{'='*70}")
        print(f"PDF INTERNALS ANALYSIS: {pdf_file}")
        print(f"{'='*70}\n")
        
        # Open with both libraries
        with pdfplumber.open(pdf_file) as pdf:
            reader = PdfReader(pdf_file)
            
            total_pages = len(pdf.pages)
            print(f"Document Information:")
            print(f"  Total Pages: {total_pages}")
            print(f"  PDF Version: {reader.pdf_header if hasattr(reader, 'pdf_header') else 'Unknown'}")
            print(f"  Encrypted: {'Yes' if reader.is_encrypted else 'No'}")
            
            # Get metadata
            metadata = reader.metadata
            if metadata:
                if metadata.get('/Title'):
                    print(f"  Title: {metadata['/Title']}")
                if metadata.get('/Author'):
                    print(f"  Author: {metadata['/Author']}")
            
            print(f"\n{'-'*70}")
            
            # Analyze fonts with multi-method approach
            print(f"\n1. FONTS")
            print(f"{'='*70}")
            fonts, font_errors, method = analyze_fonts_multi_method(reader, pdf_file)
            print(f"  Detection method: {method}")
            if not PYMUPDF_AVAILABLE:
                print(f"  ℹ Install PyMuPDF for better font detection: pip install PyMuPDF")
            if fonts:
                for font_name, pages in sorted(fonts.items()):
                    pages_str = ', '.join(map(str, pages[:10]))
                    if len(pages) > 10:
                        pages_str += f" ... ({len(pages)} pages total)"
                    print(f"  • {font_name}")
                    print(f"    Pages: {pages_str}")
            else:
                print("  No fonts found or font information unavailable.")
            if font_errors:
                print(f"  ⚠ Errors encountered: {len(font_errors)}")
                for err in font_errors[:3]:
                    print(f"    - {err}")
                if len(font_errors) > 3:
                    print(f"    ... and {len(font_errors) - 3} more")
            print(f"  Total unique fonts: {len(fonts)}")
            
            # Analyze images
            print(f"\n2. IMAGES")
            print(f"{'='*70}")
            images, image_errors = analyze_images(pdf)
            if images:
                total_images = sum(len(pages) for pages in images.values())
                for size, pages in sorted(images.items()):
                    pages_str = ', '.join(map(str, pages[:10]))
                    if len(pages) > 10:
                        pages_str += f" ... ({len(pages)} pages total)"
                    print(f"  • Size: {size} - Count: {len(pages)}")
                    print(f"    Pages: {pages_str}")
                print(f"  Total images: {total_images}")
            else:
                print("  No images found.")
                print(f"  Total images: 0")
            if image_errors:
                print(f"  ⚠ Errors encountered: {len(image_errors)}")
                for err in image_errors[:3]:
                    print(f"    - {err}")
                if len(image_errors) > 3:
                    print(f"    ... and {len(image_errors) - 3} more")
            
            # Analyze tables
            print(f"\n3. TABLES")
            print(f"{'='*70}")
            tables, table_errors = analyze_tables(pdf)
            if tables:
                total_tables = sum(len(pages) for pages in tables.values())
                for size, pages in sorted(tables.items()):
                    pages_str = ', '.join(map(str, pages[:10]))
                    if len(pages) > 10:
                        pages_str += f" ... ({len(pages)} pages total)"
                    print(f"  • Dimensions: {size} - Count: {len(pages)}")
                    print(f"    Pages: {pages_str}")
                print(f"  Total tables: {total_tables}")
            else:
                print("  No tables found.")
                print(f"  Total tables: 0")
            if table_errors:
                print(f"  ⚠ Errors encountered: {len(table_errors)}")
                for err in table_errors[:3]:
                    print(f"    - {err}")
                if len(table_errors) > 3:
                    print(f"    ... and {len(table_errors) - 3} more")
            
            # Analyze text
            print(f"\n4. TEXT CONTENT")
            print(f"{'='*70}")
            text_info, text_errors = analyze_text(pdf)
            if text_info['pages_with_text']:
                print(f"  Total characters: {text_info['total_characters']:,}")
                print(f"  Pages with text: {len(text_info['pages_with_text'])} of {total_pages}")
                if len(text_info['pages_with_text']) <= 20:
                    pages_str = ', '.join(map(str, text_info['pages_with_text']))
                    print(f"  Page numbers: {pages_str}")
            else:
                print("  No text content found.")
            if text_errors:
                print(f"  ⚠ Errors encountered: {len(text_errors)}")
                for err in text_errors[:3]:
                    print(f"    - {err}")
                if len(text_errors) > 3:
                    print(f"    ... and {len(text_errors) - 3} more")
            
            # Analyze annotations
            print(f"\n5. ANNOTATIONS")
            print(f"{'='*70}")
            annotations, annot_errors = analyze_annotations(reader)
            if annotations:
                total_annotations = sum(len(pages) for pages in annotations.values())
                for annot_type, pages in sorted(annotations.items()):
                    pages_str = ', '.join(map(str, pages[:10]))
                    if len(pages) > 10:
                        pages_str += f" ... ({len(pages)} pages total)"
                    print(f"  • Type: {annot_type} - Count: {len(pages)}")
                    print(f"    Pages: {pages_str}")
                print(f"  Total annotations: {total_annotations}")
            else:
                print("  No annotations found.")
                print(f"  Total annotations: 0")
            if annot_errors:
                print(f"  ⚠ Errors encountered: {len(annot_errors)}")
                for err in annot_errors[:3]:
                    print(f"    - {err}")
                if len(annot_errors) > 3:
                    print(f"    ... and {len(annot_errors) - 3} more")
            
            # Analyze forms
            print(f"\n6. FORM FIELDS")
            print(f"{'='*70}")
            forms, form_errors = analyze_forms(reader)
            if forms:
                total_fields = sum(len(pages) for pages in forms.values())
                for field_type, pages in sorted(forms.items()):
                    pages_str = ', '.join(map(str, set(pages)[:10]))
                    print(f"  • Type: {field_type} - Count: {len(pages)}")
                    print(f"    Pages: {pages_str}")
                print(f"  Total form fields: {total_fields}")
            else:
                print("  No form fields found.")
                print(f"  Total form fields: 0")
            if form_errors:
                print(f"  ⚠ Errors encountered: {len(form_errors)}")
                for err in form_errors[:3]:
                    print(f"    - {err}")
                if len(form_errors) > 3:
                    print(f"    ... and {len(form_errors) - 3} more")
            
            # Analyze compression
            print(f"\n7. COMPRESSION METHODS")
            print(f"{'='*70}")
            compression, compress_errors = analyze_compression(reader)
            if compression:
                for method, count in sorted(compression.items(), key=lambda x: x[1], reverse=True):
                    method_name = method.replace('/', '')
                    print(f"  • {method_name}: {count} objects")
            else:
                print("  No compression information available.")
            if compress_errors:
                print(f"  ⚠ Errors encountered: {len(compress_errors)}")
                for err in compress_errors[:3]:
                    print(f"    - {err}")
                if len(compress_errors) > 3:
                    print(f"    ... and {len(compress_errors) - 3} more")
            
            # Summary
            print(f"\n{'='*70}")
            print(f"SUMMARY")
            print(f"{'='*70}")
            print(f"  Pages: {total_pages}")
            print(f"  Fonts: {len(fonts)}")
            print(f"  Images: {sum(len(pages) for pages in images.values())}")
            print(f"  Tables: {sum(len(pages) for pages in tables.values())}")
            print(f"  Text Pages: {len(text_info['pages_with_text'])}")
            print(f"  Annotations: {sum(len(pages) for pages in annotations.values())}")
            print(f"  Form Fields: {sum(len(pages) for pages in forms.values())}")
            print(f"  Compression Methods: {len(compression)}")
            
            # Total errors
            total_errors = (len(font_errors) + len(image_errors) + len(table_errors) + 
                          len(text_errors) + len(annot_errors) + len(form_errors) + 
                          len(compress_errors))
            if total_errors > 0:
                print(f"  ⚠ Total Errors: {total_errors}")
                print(f"\n  Note: Some elements may not have been fully analyzed due to errors.")
            
            print(f"{'='*70}\n")
        
        return True
        
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_usage():
    """Print usage information."""
    script_name = os.path.basename(sys.argv[0])
    print(f"\nUsage: python {script_name} <pdf_file>")
    print("\nDescription:")
    print("  Analyzes internal elements and objects in PDF files.")
    print("  Extracts information about fonts, images, tables, text, annotations,")
    print("  form fields, and compression methods.")
    print("  Uses multiple methods for robust font extraction.")
    print("\nArguments:")
    print("  <pdf_file>     Source PDF file (mandatory)")
    print("\nExample:")
    print(f"  python {script_name} sample_file.pdf")
    print("\nNote:")
    print("  For best results, install PyMuPDF: pip install PyMuPDF\n")


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
    
    success = analyze_pdf(pdf_file)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

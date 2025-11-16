#!/usr/bin/env python3
"""
PDF Image Extractor
Extracts images from PDF files and saves to PNG or JPEG format.
Detects duplicate images across pages and saves only unique instances.
"""

import sys
import os
import hashlib
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow library not found.")
    print("Install it using: pip install Pillow")
    sys.exit(1)

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
    
    output_format = None
    source_file = None
    
    # Find output format
    if '-p' in args or '-png' in args:
        output_format = 'png'
        type_arg = '-p' if '-p' in args else '-png'
        type_index = args.index(type_arg)
        if type_index + 1 < len(args):
            source_file = args[type_index + 1]
    elif '-j' in args or '-jpeg' in args:
        output_format = 'jpeg'
        type_arg = '-j' if '-j' in args else '-jpeg'
        type_index = args.index(type_arg)
        if type_index + 1 < len(args):
            source_file = args[type_index + 1]
    else:
        print("Error: Missing output format argument (-p/-png or -j/-jpeg).")
        return None, None, False
    
    if not source_file:
        print("Error: Missing source PDF file argument.")
        return None, None, False
    
    return output_format, source_file, False


def get_image_hash(pil_image):
    """Calculate hash of image for duplicate detection."""
    # Convert to bytes
    img_byte_arr = BytesIO()
    pil_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Calculate SHA256 hash
    return hashlib.sha256(img_byte_arr).hexdigest()


def extract_images(pdf_file, output_format):
    """Extract all images from PDF file, detecting duplicates."""
    if not os.path.exists(pdf_file):
        print(f"Error: File '{pdf_file}' not found.")
        return False
    
    if not pdf_file.lower().endswith('.pdf'):
        print(f"Error: '{pdf_file}' is not a PDF file.")
        return False
    
    try:
        base_name = os.path.splitext(pdf_file)[0]
        total_images = 0
        saved_images = 0
        duplicate_count = 0
        
        # Dictionary to track image hashes and their locations
        image_hashes = {}  # hash -> {'page': int, 'img_num': int, 'pages': [list of pages]}
        
        with pdfplumber.open(pdf_file) as pdf:
            print(f"Processing {len(pdf.pages)} page(s)...")
            
            # First pass: extract all images and calculate hashes
            for page_num, page in enumerate(pdf.pages, 1):
                images = page.images
                
                if images:
                    print(f"Found {len(images)} image(s) on page {page_num}")
                    
                    for img_num, img in enumerate(images, 1):
                        try:
                            # Extract image coordinates
                            x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']
                            
                            # Crop image from page
                            cropped_page = page.crop((x0, y0, x1, y1))
                            img_obj = cropped_page.to_image(resolution=300)
                            
                            # Convert to PIL Image
                            pil_image = img_obj.original
                            
                            # Handle RGBA for JPEG
                            if output_format == 'jpeg' and pil_image.mode == 'RGBA':
                                pil_image = pil_image.convert('RGB')
                            
                            # Calculate image hash
                            img_hash = get_image_hash(pil_image)
                            
                            total_images += 1
                            
                            # Check if this image already exists
                            if img_hash in image_hashes:
                                # Duplicate found
                                image_hashes[img_hash]['pages'].append(page_num)
                                duplicate_count += 1
                                print(f"  Image {img_num} on page {page_num} is a duplicate (first seen on page {image_hashes[img_hash]['page']})")
                            else:
                                # New unique image
                                image_hashes[img_hash] = {
                                    'image': pil_image,
                                    'page': page_num,
                                    'img_num': img_num,
                                    'pages': [page_num]
                                }
                            
                        except Exception as e:
                            print(f"  Warning: Could not extract image {img_num} on page {page_num}: {e}")
            
            # Second pass: save unique images
            print(f"\nSaving unique images...")
            for img_hash, img_data in image_hashes.items():
                pil_image = img_data['image']
                page_num = img_data['page']
                img_num = img_data['img_num']
                pages = img_data['pages']
                
                # Determine if image appears on multiple pages
                if len(pages) > 1:
                    # Image appears on multiple pages
                    output_file = f"{base_name}_page_{page_num:02d}_image_{img_num:02d}_multi.{output_format}"
                    print(f"  Saved: {output_file} (appears on pages: {', '.join(map(str, pages))})")
                else:
                    # Image appears on single page only
                    output_file = f"{base_name}_page_{page_num:02d}_image_{img_num:02d}.{output_format}"
                    print(f"  Saved: {output_file}")
                
                # Save image
                pil_image.save(output_file, format=output_format.upper())
                saved_images += 1
        
        print(f"\nSummary:")
        print(f"  Total images found: {total_images}")
        print(f"  Unique images saved: {saved_images}")
        print(f"  Duplicate images skipped: {duplicate_count}")
        
        if saved_images == 0:
            print("No images found in PDF.")
        
        return True
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


def print_usage():
    """Print usage information."""
    script_name = os.path.basename(sys.argv[0])
    print(f"\nUsage: python {script_name} <-p|-png|-j|-jpeg> <pdf_file>")
    print("\nDescription:")
    print("  Extracts images from PDF files and saves to PNG or JPEG format.")
    print("  Automatically detects duplicate images across pages and saves only unique instances.")
    print("\nArguments:")
    print("  -p, -png       Output in PNG format (mandatory)")
    print("  -j, -jpeg      Output in JPEG format (mandatory)")
    print("  <pdf_file>     Source PDF file (mandatory)")
    print("\nOutput naming:")
    print("  Unique image:    [source]_page_[NN]_image_[NN].[format]")
    print("  Multi-page:      [source]_page_[NN]_image_[NN]_multi.[format]")
    print("\nExamples:")
    print(f"  python {script_name} -p sample_file.pdf")
    print(f"  python {script_name} -png sample_file.pdf")
    print(f"  python {script_name} -j sample_file.pdf")
    print(f"  python {script_name} -jpeg sample_file.pdf\n")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("\nError: No arguments provided.")
        print_usage()
        sys.exit(1)
    
    output_format, source_file, show_help = parse_arguments()
    
    if show_help:
        print_usage()
        sys.exit(0)
    
    if output_format is None or source_file is None:
        print_usage()
        sys.exit(1)
    
    success = extract_images(source_file, output_format)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

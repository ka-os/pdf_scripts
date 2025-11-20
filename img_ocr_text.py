import os
import sys
import argparse
from PIL import Image
import pytesseract
from fpdf import FPDF

def perform_ocr(image_path):
    """
    Performs OCR on a single image file and returns the extracted text.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except FileNotFoundError:
        print(f"Error: Source file not found at '{image_path}'", file=sys.stderr)
    except Exception as e:
        print(f"Error processing image '{image_path}': {e}", file=sys.stderr)
    return None

def save_as_pdf(text, output_path):
    """
    Saves the extracted text as a searchable PDF.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        # Add a Unicode font (DejaVu) to support a wide range of characters
        pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 5, text)
        pdf.output(output_path)
        print(f"  -> Successfully saved PDF to '{output_path}'")
    except Exception as e:
        # Fallback for systems without DejaVu font installed
        if "FPDF error: Can't open font file" in str(e):
            try:
                print("  -> DejaVu font not found. Falling back to Arial (may not support all characters).")
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 5, text)
                pdf.output(output_path)
                print(f"  -> Successfully saved PDF to '{output_path}'")
            except Exception as fallback_e:
                print(f"  -> Error creating PDF with fallback font: {fallback_e}", file=sys.stderr)
        else:
            print(f"  -> Error creating PDF: {e}", file=sys.stderr)


def get_files_from_directory(dir_path, process_png, process_jpg):
    """
    Gathers a list of image files from a directory based on format flags.
    """
    if not os.path.isdir(dir_path):
        print(f"Error: Directory not found at '{dir_path}'", file=sys.stderr)
        sys.exit(1)

    supported_extensions = []
    if process_png:
        supported_extensions.append('.png')
    if process_jpg:
        supported_extensions.append('.jpg')
        supported_extensions.append('.jpeg')
    
    if not supported_extensions:
        supported_extensions.extend(['.png', '.jpg', '.jpeg'])

    files_to_process = []
    for filename in os.listdir(dir_path):
        if any(filename.lower().endswith(ext) for ext in supported_extensions):
            files_to_process.append(os.path.join(dir_path, filename))
    return files_to_process

def main():
    """
    Main function to parse arguments and orchestrate the OCR process.
    """
    parser = argparse.ArgumentParser(
        description="Extract text from images using OCR and save as .txt or searchable .pdf.",
        epilog="Examples:\n"
               "  python img_ocr_text.py -t file1.png file2.jpg\n"
               "  python img_ocr_text.py -p files_to_read.txt\n"
               "  python img_ocr_text.py -p -d ./images_folder\n",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Mandatory output format group
    output_format_group = parser.add_mutually_exclusive_group(required=True)
    output_format_group.add_argument(
        '-t', '--text',
        action='store_true',
        help="Output extracted text to a .txt file."
    )
    output_format_group.add_argument(
        '-p', '--pdf',
        action='store_true',
        help="Output extracted text to a searchable .pdf file."
    )

    # Input sources
    parser.add_argument(
        '-d', '--dir',
        dest='directory',
        help="Path to a directory with image files to process."
    )
    parser.add_argument(
        'inputs',
        nargs='*',
        help="One or more image files, or a single .txt file listing image files."
    )
    
    # Filters for directory mode
    parser.add_argument(
        '--png',
        action='store_true',
        help="Process only PNG files when using -d."
    )
    parser.add_argument(
        '--jpg',
        action='store_true',
        help="Process only JPG/JPEG files when using -d."
    )

    args = parser.parse_args()

    if not args.directory and not args.inputs:
        parser.print_help()
        print("\nError: You must provide at least one input file, a .txt file list, or a directory with -d.", file=sys.stderr)
        sys.exit(1)

    if args.directory and args.inputs:
        print("\nError: You can specify a directory with -d OR a list of files, but not both.", file=sys.stderr)
        sys.exit(1)

    files_to_process = []
    if args.directory:
        # Note: The original -p and -j flags are now --png and --jpg to avoid conflict
        files_to_process = get_files_from_directory(args.directory, args.png, args.jpg)
    elif args.inputs:
        first_input = args.inputs[0]
        if len(args.inputs) == 1 and first_input.lower().endswith('.txt'):
            try:
                with open(first_input, 'r') as f:
                    files_to_process = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"Error: The file list '{first_input}' was not found.", file=sys.stderr)
                sys.exit(1)
        else:
            files_to_process = args.inputs

    if not files_to_process:
        print("No image files found to process.", file=sys.stderr)
        sys.exit(0)

    print(f"Found {len(files_to_process)} file(s) to process...")

    for image_path in files_to_process:
        print(f"Processing '{image_path}'...")
        text = perform_ocr(image_path)

        if text is not None:
            filtered_lines = [line for line in text.splitlines() if line.strip()]
            filtered_text = "\n".join(filtered_lines)
            
            base, _ = os.path.splitext(image_path)

            if args.text:
                output_path = base + '.txt'
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(filtered_text)
                    print(f"  -> Successfully saved text to '{output_path}'")
                except Exception as e:
                    print(f"  -> Error writing to file '{output_path}': {e}", file=sys.stderr)
            
            elif args.pdf:
                output_path = base + '.pdf'
                save_as_pdf(filtered_text, output_path)

if __name__ == "__main__":
    main()
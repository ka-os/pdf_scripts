
import os
import sys
import argparse
from PIL import Image
import pytesseract

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
    
    # If no format is specified, process both
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
        description="Extract text from images using OCR.",
        epilog="""Examples:
               python img_ocr_text.py file1.png file2.jpg
               python img_ocr_text.py files_to_read.txt
               python img_ocr_text.py -d ./images_folder
               python img_ocr_text.py -d ./images -p  (only PNGs)
               python img_ocr_text.py -d ./images -j  (only JPGs)""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-d', '--dir',
        dest='directory',
        help="Path to a directory with image files to process."
    )
    parser.add_argument(
        '-p', '--png',
        action='store_true',
        help="Process only PNG files when using -d."
    )
    parser.add_argument(
        '-j', '--jpg',
        action='store_true',
        help="Process only JPG/JPEG files when using -d."
    )
    parser.add_argument(
        'inputs',
        nargs='*',
        help="One or more image files, or a single .txt file listing image files."
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
            # Filter out empty lines
            filtered_lines = [line for line in text.splitlines() if line.strip()]
            filtered_text = "\n".join(filtered_lines)

            base, _ = os.path.splitext(image_path)
            output_path = base + '.txt'
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(filtered_text)
                print(f"  -> Successfully saved text to '{output_path}'")
            except Exception as e:
                print(f"  -> Error writing to file '{output_path}': {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

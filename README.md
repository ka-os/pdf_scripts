# PDF Processing Scripts

A collection of Python scripts for common PDF operations: extracting metadata, splitting, and merging PDF files.

## Requirements

### Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains:
- **pypdf** (>=4.0.0) - Core library for PDF reading, writing, and manipulation
- **pdfplumber** (>=0.10.0) - PDF table and image extraction with document layout analysis
- **Pillow** (>=10.0.0) - Image processing and format conversion
- **PyMuPDF** (>=1.23.0) - High-performance PDF library for robust font extraction and analysis (highly recommended for pdf_internals.py)
- **pytesseract** (>=0.3.10) - OCR library for image-to-text extraction (used in img_ocr_text.py)
- **fpdf2** (>=2.7.0) - Library to create PDF documents from text (used in img_ocr_text.py)

### System Requirements

- Python 3.7 or higher
- pip (Python package installer)
- **Tesseract-OCR Engine** - Required for `img_ocr_text.py`. See installation instructions for your OS.

### Recommended Setup

Use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Scripts

### 1. pdf_metadata.py

Extracts and displays metadata from PDF files.

**Description:**
Reads a PDF file and displays all available metadata including title, author, subject, creator, producer, creation date, modification date, keywords, file size, page count, and encryption status.

**Arguments:**
- `<pdf_file>` - Path to PDF file (mandatory)

**Usage:**

```bash
python pdf_metadata.py document.pdf
python pdf_metadata.py /path/to/file.pdf
```

**Output:**
Displays formatted metadata information in the terminal.

---

### 2. pdf_split.py

Splits a PDF file into individual single-page files.

**Description:**
Takes a PDF file and creates separate PDF files for each page. Each output file contains exactly one page from the source document.

**Arguments:**
- `<pdf_file>` - Path to PDF file to split (mandatory)

**Naming Convention:**
- Output files: `filename_page_01.pdf`, `filename_page_02.pdf`, etc.
- Single-digit page numbers use leading zeros (01-09)

**Usage:**

```bash
python pdf_split.py sample_file.pdf
```

**Example:**
If `sample_file.pdf` has 15 pages, creates:
- `sample_file_page_01.pdf` through `sample_file_page_15.pdf`

---

### 3. pdf_multi_split.py

Splits a PDF file at specified page numbers into multiple files.

**Description:**
Divides a PDF file into multiple segments at specified page numbers. Creates n+1 output files for n split points.

**Arguments:**
- `<pdf_file>` - Path to PDF file to split (mandatory)
- `<split_points>` - Page number(s) where splits occur, comma-separated (mandatory)

**Naming Convention:**
- Output files: `filename_pages_01_07.pdf`, `filename_pages_08_11.pdf`, etc.
- Format: `[name]_pages_[first]_[last].pdf`
- Single-digit page numbers use leading zeros

**Usage:**

```bash
# Single split point
python pdf_multi_split.py sample_file.pdf 7

# Multiple split points
python pdf_multi_split.py sample_file.pdf 7,11
```

**Examples:**

Split at page 7 (15-page document):
```bash
python pdf_multi_split.py sample_file.pdf 7
```
Creates:
- `sample_file_pages_01_07.pdf` (pages 1-7)
- `sample_file_pages_08_15.pdf` (pages 8-15)

Split at pages 7 and 11:
```bash
python pdf_multi_split.py sample_file.pdf 7,11
```
Creates:
- `sample_file_pages_01_07.pdf` (pages 1-7)
- `sample_file_pages_08_11.pdf` (pages 8-11)
- `sample_file_pages_12_15.pdf` (pages 12-15)

---

### 4. pdf_merge.py

Merges multiple PDF files into a single file.

**Description:**
Combines multiple PDF files into one output file, preserving the order of input files as specified.

**Arguments:**
- `-o <output_file>` - Output filename (mandatory)
- `-s <source_files>` - Source PDF files to merge (mandatory, one or more)

**Notes:**
- The `.pdf` extension is automatically added to output filename if not specified
- Source files are merged in the order provided
- At least one source file must be specified

**Usage:**

```bash
# Merge two files
python pdf_merge.py -o merged.pdf -s file1.pdf file2.pdf

# Merge three files
python pdf_merge.py -o new_file -s sample1.pdf sample2.pdf sample3.pdf

# Merge multiple files
python pdf_merge.py -o combined.pdf -s doc1.pdf doc2.pdf doc3.pdf doc4.pdf
```

**Example:**
```bash
python pdf_merge.py -o report.pdf -s cover.pdf content.pdf appendix.pdf
```
Creates `report.pdf` containing all three files merged in order.

---

### 5. pdf_extract_table.py

Extracts tables from PDF files and outputs to TXT or HTML format.

**Description:**
Uses document layout analysis to identify and extract only tables from PDF files. Ignores all other content types. Each table is labeled with its page number.

**Arguments:**
- `-t` or `-txt` - Output in plain text format (mandatory)
- `-h` or `-html` - Output in HTML format (mandatory)
- `<pdf_file>` - Source PDF file (mandatory)

**Naming Convention:**
- Text output: `[source_name]_tables.txt`
- HTML output: `[source_name]_tables.html`

**Usage:**

```bash
# Extract to text format
python pdf_extract_table.py -t sample_file.pdf
python pdf_extract_table.py -txt sample_file.pdf

# Extract to HTML format
python pdf_extract_table.py -h sample_file.pdf
python pdf_extract_table.py -html sample_file.pdf
```

**Output:**
- Text format: Tables formatted with column alignment and separators
- HTML format: Styled HTML tables with alternating row colors

**Example:**
```bash
python pdf_extract_table.py -h report.pdf
```
Creates `report_tables.html` containing all tables found in the PDF.

---

### 6. pdf_extract_image.py

Extracts images from PDF files and saves to PNG or JPEG format with automatic duplicate detection.

**Description:**
Uses document layout analysis to identify and extract only images from PDF files. Automatically detects duplicate images across pages using SHA256 hash comparison and saves only unique instances. Images appearing on multiple pages are marked with `_multi` suffix.

**Arguments:**
- `-p` or `-png` - Output in PNG format (mandatory)
- `-j` or `-jpeg` - Output in JPEG format (mandatory)
- `<pdf_file>` - Source PDF file (mandatory)

**Naming Convention:**
- Single page image: `[source]_page_[NN]_image_[NN].[format]`
- Multi-page image: `[source]_page_[NN]_image_[NN]_multi.[format]`
- Page and image numbers use zero-padding (01, 02, etc.)
- Page number refers to the first occurrence of the image

**Usage:**

```bash
# Extract to PNG format
python pdf_extract_image.py -p sample_file.pdf
python pdf_extract_image.py -png sample_file.pdf

# Extract to JPEG format
python pdf_extract_image.py -j sample_file.pdf
python pdf_extract_image.py -jpeg sample_file.pdf
```

**Output Examples:**
- `sample_file_page_01_image_01.png` (unique image on page 1)
- `sample_file_page_01_image_02_multi.png` (image appears on pages 1, 2, 3)
- `sample_file_page_03_image_01.jpeg` (unique image on page 3)

**Features:**
- Extracts at 300 DPI resolution
- Automatic duplicate detection across all pages
- Reports which pages contain duplicate images
- Handles RGBA to RGB conversion for JPEG format
- Displays summary statistics (total, unique, duplicates)
- Preserves image quality

**Example:**
```bash
python pdf_extract_image.py -p report.pdf
```
Output:
```
Processing 10 page(s)...
Found 3 image(s) on page 1
Found 2 image(s) on page 5
  Image 1 on page 5 is a duplicate (first seen on page 1)

Saving unique images...
  Saved: report_page_01_image_01_multi.png (appears on pages: 1, 5)
  Saved: report_page_01_image_02.png
  Saved: report_page_01_image_03.png
  Saved: report_page_05_image_02.png

Summary:
  Total images found: 5
  Unique images saved: 4
  Duplicate images skipped: 1
```

---

### 7. pdf_internals.py

Analyzes internal PDF structure and extracts detailed information about all elements and objects.

**Description:**
Comprehensive PDF analysis tool that examines fonts, images, tables, text content, annotations, form fields, and compression methods. Uses multiple detection methods for robust font extraction, including PyMuPDF for handling malformed PDFs.

**Arguments:**
- `<pdf_file>` - Source PDF file (mandatory)

**Features:**
- **Multi-method font detection**: Tries PyMuPDF, direct dictionary access, and content stream parsing
- **Detailed font information**: Base font, subtype, encoding, embedded status
- **Error resilience**: Continues analysis even with corrupted or malformed PDFs
- **Comprehensive reporting**: Page-by-page breakdown with error tracking
- **Summary statistics**: Total counts and error summary

**Usage:**

```bash
python pdf_internals.py sample_file.pdf
```

**Output Sections:**

1. **Document Information** - Pages, PDF version, encryption status, metadata
2. **Fonts** - Font names, types, encodings, pages where used
3. **Images** - Image dimensions and locations
4. **Tables** - Table dimensions and locations
5. **Text Content** - Character count and text-containing pages
6. **Annotations** - Comment, highlight, and markup types
7. **Form Fields** - Interactive form field types
8. **Compression Methods** - Filters used (FlateDecode, DCTDecode, etc.)
9. **Summary** - Aggregate statistics and error count

**Example Output:**

```
======================================================================
PDF INTERNALS ANALYSIS: document.pdf
======================================================================

Document Information:
  Total Pages: 17
  PDF Version: %PDF-1.7
  Encrypted: No
  Title: Sample Document

----------------------------------------------------------------------

1. FONTS
======================================================================
  Detection method: PyMuPDF
  • Helvetica (Type1) - WinAnsiEncoding
    Pages: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ... (15 pages total)
  • Arial-BoldMT (TrueType) [Embedded]
    Pages: 1, 3, 5
  Total unique fonts: 2

2. IMAGES
======================================================================
  • Size: 1920x1080px - Count: 3
    Pages: 1, 5, 10
  Total images: 3

[... continues with other sections ...]

SUMMARY
======================================================================
  Pages: 17
  Fonts: 2
  Images: 3
  Tables: 1
  Text Pages: 17
  Annotations: 0
  Form Fields: 0
  Compression Methods: 2
```

**Font Detection Methods:**

The script tries three methods in order:

1. **PyMuPDF (Recommended)** - Most reliable, handles malformed PDFs
   - Install: `pip install PyMuPDF`
   - Extracts embedded font information
   - Works with damaged or non-standard PDFs

2. **Direct Dictionary Access** - Fallback for standard PDFs
   - Accesses `/Resources/Font` directly
   - Reads font descriptors
   
3. **Content Stream Parsing** - Last resort
   - Parses content streams for `Tf` operators
   - Matches font references to resources

**Handling Errors:**

The script gracefully handles:
- Missing or corrupted font information
- Broken object references
- Malformed page structures
- Incomplete metadata
- Damaged compression streams

Errors are reported but don't stop analysis. Each section shows:
- Successfully extracted data
- Error count and sample error messages
- Summary of what couldn't be analyzed

**Installation Note:**

For best results with problematic PDFs, install PyMuPDF:
```bash
pip install PyMuPDF
```

Without PyMuPDF, the script uses fallback methods but may miss fonts in malformed PDFs.

---

### 8. pdf_extract_text.py

Extracts all text and table content from PDF files to TXT format.

**Description:**
Comprehensive text extraction tool that extracts both regular text and formatted tables from PDF files using document layout analysis. Preserves document structure with page markers and formatted tables.

**Arguments:**
- `<pdf_file>` - Source PDF file (mandatory)

**Naming Convention:**
- Output file: `[source_name].txt`

**Usage:**

```bash
python pdf_extract_text.py sample_file.pdf
python pdf_extract_text.py document.pdf
```

**Output Format:**

The TXT file includes:
- **Page headers** - Clear page number markers
- **Text content** - All extracted text from each page
- **Formatted tables** - Tables with column alignment and separators
- **Error markers** - Notation where extraction failed

**Example Output:**

```
======================================================================
PAGE 1
======================================================================

This is the text content from the first page of the PDF document.
It includes all paragraphs and text elements.

----------------------------------------------------------------------
TABLE 1 (Page 1)
----------------------------------------------------------------------
Name      | Age  | City        
John Doe  | 30   | New York    
Jane Smith| 25   | Los Angeles 

======================================================================
PAGE 2
======================================================================

Text content from page 2...
```

**Features:**
- Preserves page structure and order
- Formats tables with column alignment
- Handles multi-page documents
- Uses document layout analysis for accurate extraction
- Error handling with descriptive messages
- Automatic UTF-8 encoding for international characters

**Example:**
```bash
python pdf_extract_text.py report.pdf
```
Output:
```
Processing 10 page(s)...
  Extracting page 1...
  Extracting page 2...
  ...
  Extracting page 10...

Text extracted successfully!
Output saved to: report.txt
```

---

### 9. img_ocr_text.py

Extracts text from image files using OCR and saves it as a `.txt` or searchable `.pdf` file.

**Description:**
Reads image files (PNG, JPG/JPEG), extracts text using OCR, and saves the output in the format specified. The script requires a mandatory output format flag (`-t` for text or `-p` for PDF). Empty lines are removed from the extracted text.

**Dependencies:**
- This script requires Google's Tesseract-OCR engine to be installed on your system.
- It also uses the `fpdf2` library for PDF creation, which can be installed from `requirements.txt`.

**Arguments:**

*   **Output Format (Mandatory):**
    *   `-t` or `--text`: Output extracted text to a `.txt` file.
    *   `-p` or `--pdf`: Output extracted text to a searchable `.pdf` file.

*   **Input Source (Choose one):**
    *   `<source_files>`: One or more source image files (e.g., `file1.png file2.jpg`).
    *   `<text_file_list>`: A single `.txt` file containing image file paths (one per line).
    *   `-d` or `--dir <directory>`: Path to a directory containing image files.

*   **Directory Filters (Optional, for use with `-d`):**
    *   `--png`: Process only PNG files.
    *   `--jpg`: Process only JPG/JPEG files.

**Naming Convention:**
- Text output: `[source_image_name].txt`
- PDF output: `[source_image_name].pdf`

**Usage:**

```bash
# Create a .txt file from an image
python img_ocr_text.py -t my_image.png

# Create a searchable .pdf file from an image
python img_ocr_text.py -p my_image.png

# Create .pdf files for all images in a directory
python img_ocr_text.py -p -d ./image_folder

# Create .txt files for only JPG images in a directory
python img_ocr_text.py -t -d ./image_folder --jpg

# Process a list of images from a text file, creating PDFs
python img_ocr_text.py -p list_of_images.txt
```

---

## License

MIT License

## Contributing

Feel free to submit issues and enhancement requests.

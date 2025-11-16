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

### System Requirements

- Python 3.7 or higher
- pip (Python package installer)

### Recommended Setup

Use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

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

## License

MIT License

## Contributing

Feel free to submit issues and enhancement requests.

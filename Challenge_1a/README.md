# Challenge 1a: PDF Header Extraction Solution

## Overview
This is a solution for Challenge 1a of the Adobe India Hackathon 2025. The challenge requires implementing a PDF processing solution that extracts structured data from PDF documents and outputs JSON files. The solution is containerized using Docker.

## Solution Structure
```
Challenge_1a/
├── sample_dataset/
│   ├── outputs/         # JSON files provided as outputs.
│   ├── pdfs/            # Input PDF files
│   └── schema/          # Output schema definition
│       └── output_schema.json
├── Dockerfile           # Docker container configuration
├── process_pdfs.py      # processing script
├── extract_from_pdf.py  # Script with processing logic
└── README.md           # This file
```

### Build Command
```bash
docker build --platform linux/amd64 -t pdf-outline-extractor .
```

### Run Command
```bash
docker run --rm 
  -v "$(pwd)/input":/app/input:ro \
  -v "$(pwd)/output":/app/output \
  --network none pdf-outline-extractor
```

### Caution While Executing
1. Make sure docker image is built
2. Replace input output directories accordingly

## Methods Used
This project extracts structured outlines (headers and content) from PDFs using a set of heuristic-based rules designed to handle varying document layouts. The classification of headers into H1, H2, H3, and H4 is determined by analyzing visual and structural features from the PDF text content.

### Techniques & Rules Applied:
#### Font Size-Based Hierarchy
* The algorithm computes the most common font size (i.e., body text) on each page.
* Lines with significantly larger font sizes are candidates for headers (e.g., H1 > H2 > H3 > H4).
* Predefined thresholds are applied to detect H1–H4.

#### Boldness Detection
* If font sizes are not sufficient for separation, bold text is used as a secondary signal.
* For example, bold lines that are visually prominent (e.g., wide padding or top-aligned) are elevated as header candidates.

#### Indentation & Padding
* Left padding (x0) and right padding (page_width - x1) are analyzed to detect structure and alignment.
* Consistent left alignment helps distinguish H3 and H4 under H2.

#### Title Skipping
* The first title (e.g., document title) is excluded from being labeled as a header to avoid duplication.

#### Fallbacks and Adjustments
* If font sizes are homogeneous across the document, the system falls back to boldness + padding-based detection.
* Special characters (like bullets •) and duplicate headers are cleaned or merged as needed.
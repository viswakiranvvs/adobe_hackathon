# Challenge 1a: PDF Processing Solution

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
├── process_pdfs.py      # Sample processing script
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
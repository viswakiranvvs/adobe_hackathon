# Challenge 1b: PDF Summarizer Solution

## Overview
This is a solution for Challenge 1b of the Adobe India Hackathon 2025. The challenge requires implementing a PDF summarizing solution that extracts structured data from PDF documents, understands sections and answer the job based on persona. The solution is containerized using Docker.

## Solution Structure
```
Challenge_1b/
├── Collection x/
│   ├── _input.json/     # Input JSON file
│   ├── PDFs/            # Input PDF files
├── Dockerfile           # Docker container configuration
├── summarize_pdfs.py    # processing script
├── extract_from_pdf.py  # Script with processing logic from 1a
├── sllm_download.py     # Script that processes sllm
└── README.md            # This file
```

### Build Command
```bash
docker build --platform linux/amd64 -t pdf-summarizer .
```

### Run Command
```bash
docker run --rm \                                      
  -v "$(pwd)/Collection 3/":/app/input/Collection:rw \
  --network none \
  pdf-summarize
```

### Caution While Executing
1. Make sure docker image is built
2. Replace input output directories accordingly

## Methods Used
This project performs document section ranking and summarization using lightweight, CPU-friendly language models. The pipeline is fully offline and meets the following constraints:

CPU-only execution
Model size ≤ 1GB
Processing time ≤ 60 seconds for 3–5 documents
No internet access during execution

### 1. Section Ranking
We use a pre-trained sentence embedding model to compute similarity between the user-defined persona/task and each section's title:

#### Model: all-MiniLM-L6-v2 from sentence-transformers (≈80MB)
Approach:
* Encode the combined prompt (persona + job description)
* Encode each section title
* Compute cosine similarity to rank relevance

### 2. Summarization
Top-ranked sections are summarized using a small transformer-based language model:

#### Model: t5-small from HuggingFace Transformers (≈220MB)
Approach:
* Tokenize and truncate long texts
* Use prefix "summarize: " for prompt-based generation
* Generate concise summaries of 40–120 tokens

### 3. Output Structure
The final output is a JSON object containing:
* metadata: including documents used, persona, task, and timestamp
* extracted_sections: top-ranked sections with document names and page numbers
* subsection_analysis: summaries for each top section
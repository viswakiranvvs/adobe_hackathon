from PyPDF2 import PdfReader
import pdfplumber

file_path='/home/robotics-pc-20/Documents/Viswa/adobe_hackathon/test_pdfs/ME5083Lec22.pdf'
reader = PdfReader(file_path)
title = reader.metadata.title
print(title)

headings = []
with pdfplumber.open(file_path) as pdf:
    for page_num, page in enumerate(pdf.pages, 1):
        for char in page.chars:
            if float(char["size"]) > 16:  # Adjust font size threshold as needed
                headings.append((page_num, char["text"]))
print(headings)

with pdfplumber.open(file_path) as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"Page {i+1}")

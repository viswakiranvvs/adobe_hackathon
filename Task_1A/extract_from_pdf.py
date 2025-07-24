from PyPDF2 import PdfReader
import pdfplumber

# file_path='/home/robotics-pc-20/Documents/Viswa/adobe_hackathon/test_pdfs/ME5083Lec22.pdf'
file_path='/home/robotics-pc-20/Documents/Viswa/adobe_hackathon/Adobe-India-Hackathon25/Challenge_1a/sample_dataset/pdfs/file03.pdf'


# reader = PdfReader(file_path)
# title = reader.metadata.title
# print(title)

# headings = []
# font_sizes = set()
# with pdfplumber.open(file_path) as pdf:
#     for page_num, page in enumerate(pdf.pages, 1):
#         print(page_num)
#         print(page.chars[0])
#         print(page.chars[1])
#         for char in page.chars:
#             font_sizes.add(int(char["size"]))
#             if float(char["size"]) > 16:  # Adjust font size threshold as needed
#                 headings.append((page_num, char["text"]))
# # print(headings)
# print(font_sizes)

# with pdfplumber.open(file_path) as pdf:
#     for i, page in enumerate(pdf.pages):
#         print(f"Page {i+1}")

import pdfplumber
from collections import defaultdict, Counter

# file_path = "your-file.pdf"

font_sizes = set()
sentences_by_page_and_size = defaultdict(lambda: defaultdict(list))

with pdfplumber.open(file_path) as pdf:
    for page_num, page in enumerate(pdf.pages, 1):
        chars_by_size = defaultdict(list)
        for char in page.chars:
            fs = round(char["size"], 2)
            font_sizes.add(fs)
            chars_by_size[fs].append(char)
        for fs, chars in chars_by_size.items():
            chars = sorted(chars, key=lambda c: (c["top"], c["x0"]))
            lines = []
            current_line = []
            last_top = None
            line_threshold = 2

            for char in chars:
                if last_top is not None and abs(char["top"] - last_top) > line_threshold:
                    line_text = ""
                    prev_char = None
                    for c in current_line:
                        if prev_char is not None:
                            gap = c["x0"] - prev_char["x1"]
                            if gap > 1.5:
                                line_text += " "
                        line_text += c["text"]
                        prev_char = c
                    if line_text.strip():
                        lines.append(line_text.strip())
                    current_line = []
                current_line.append(char)
                last_top = char["top"]
            if current_line:
                line_text = ""
                prev_char = None
                for c in current_line:
                    if prev_char is not None:
                        gap = c["x0"] - prev_char["x1"]
                        if gap > 1.5:
                            line_text += " "
                    line_text += c["text"]
                    prev_char = c
                if line_text.strip():
                    lines.append(line_text.strip())
            sentences_by_page_and_size[page_num][fs] = lines

# Determine H1, H2 by font size frequency (top 2 largest font sizes are usually titles/headings)
sorted_font_sizes = sorted(font_sizes, reverse=True)
h1_size = sorted_font_sizes[0]
h2_size = sorted_font_sizes[1] if len(sorted_font_sizes) > 1 else sorted_font_sizes[0]

outline = []
title = ""

for page_num in sorted(sentences_by_page_and_size):
    for fs in sorted(sentences_by_page_and_size[page_num], reverse=True):
        for line in sentences_by_page_and_size[page_num][fs]:
            entry = {"text": line, "page": page_num-1}  # zero-based page num for compatibility
            if fs == h1_size:
                if not title:  # Use the first H1 as title
                    title = line
                entry["level"] = "H1"
                outline.append(entry)
            elif fs == h2_size:
                entry["level"] = "H2"
                outline.append(entry)

result = {
    "title": title,
    "outline": outline
}

import json
print(json.dumps(result, indent=2))
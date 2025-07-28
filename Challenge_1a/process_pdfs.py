import os
import json
from pathlib import Path

from extract_from_pdf import Task_1A

def process_pdfs():
    # Get input and output directories
    input_dir = Path("/app/input")
    output_dir = Path("/app/outputs")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    temp = Task_1A()
    
    for pdf_file in pdf_files:
        parsedData = temp.parseText(pdf_file,False)
        
        # Create output JSON file
        # print(parsedData)
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w") as f:
            print(f"Writing to {output_file}")
            # print(f"parsedData (type: {type(parsedData)})")
            json.dump(parsedData, f, indent=2)
        
        print(f"Processed {pdf_file.name} -> {output_file.name}")

if __name__ == "__main__":
    print("Starting processing pdfs")
    process_pdfs() 
    print("completed processing pdfs")
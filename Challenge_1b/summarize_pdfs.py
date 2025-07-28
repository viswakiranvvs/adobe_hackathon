from sllm_run import Task_1B
from extract_from_pdf import Task_1A
from pathlib import Path
import os
import json

def summarize():
    input_dir = Path("/app/input/Collection")
    input_data,input_filename=read_input_json(input_dir)
    # print(json.dumps(input_data,indent=2))
    # print(json.dumps(extract_fields(input_data),indent=2))
    extracted = extract_fields(input_data)
    task1a_handler = Task_1A()
    all_sections = []
    # print(extracted)
    for doc in extracted["documents"]:
        # print(doc)
        parsedText = task1a_handler.parseText(input_dir / "PDFs" / doc,True)
        all_sections.extend(build_all_sections_with_merging(parsedText,doc))
        # print(json.dumps(parsedText,indent=2))
        # print(json.dumps(build_all_sections(abc,doc),indent=2))
        # break

    # print(json.dumps(all_sections,indent=2))
    task1b_handler = Task_1B()
    output = task1b_handler.process_sections(all_sections,extracted["persona"],extracted["task"])
    output_file_name = input_filename.replace("input.json","output.json")
    output_file = input_dir / output_file_name
    with open(output_file, "w") as f:
        print(f"Writing to {output_file}")
        # print(f"parsedData (type: {type(parsedData)})")
        json.dump(output, f, indent=2)

    # print(output)

def read_input_json(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith("input.json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data,filename  # or return file_path if you just need path

    raise FileNotFoundError("No file ending with 'input.json' found in the folder.")

def extract_fields(input_data):
    # Extract document filenames and titles
    documents = [doc['filename'] for doc in input_data.get('documents', [])]
    titles = [doc['title'] for doc in input_data.get('documents', [])]

    # Extract persona
    persona = input_data.get('persona', {}).get('role', '')

    # Extract job to be done task
    task = input_data.get('job_to_be_done', {}).get('task', '')

    return {
        "documents": documents,
        "titles": titles,
        "persona": persona,
        "task": task
    }

def build_all_sections(input_json, document_filename):
    """
    Converts input outline structure into all_sections list format.
    """
    all_sections = []

    for section in input_json.get("outline", []):
        all_sections.append({
            "document": document_filename,
            "section_title": section["text"].strip(),
            "page": section["page"],
            "text": section.get("content", "")
        })

    return all_sections

def build_all_sections_with_merging(input_json, document_filename):
    """
    Merges H1 sections and their nested H2/H3/H4/None children into one combined text block.
    """
    all_sections = []
    current_section = None

    for item in input_json.get("outline", []):
        level = item.get("level")
        text = item.get("text", "").strip()
        page = item.get("page", 1)
        content = item.get("content", "").strip()

        # print(level,text,page,content)

        if level == "H1":
            # Save the current section if exists
            if current_section:
                all_sections.append(current_section)

            # Start a new H1 section
            current_section = {
                "document": document_filename,
                "section_title": text,
                "page": page,
                "text": content
            }

        elif level in ("H2", "H3", "H4") and current_section:
            # Append subsection title and content
            if text:
                current_section["text"] += f"\n\n{text}"
            if content:
                current_section["text"] += f"\n{content}"

        elif level is None and current_section:
            # Just add raw body text
            if text:
                current_section["text"] += f"\n{text}"

    # Save the final section
    if current_section:
        all_sections.append(current_section)
    # print(all_sections)

    return all_sections




if __name__ == "__main__":
    print("Starting processing pdfs")
    summarize() 
    print("completed processing pdfs")
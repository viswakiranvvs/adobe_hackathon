import pdfplumber
from collections import defaultdict
import json

class Task_1A():
    def __init__(self):
        pass

    def remove_whole_line_duplication(self,text: str) -> str:
        s = text.split(" ")
        if not s:
            return s
        # If the string length is even and the first half equals the second half
        mid = len(s) // 2
        if len(s) % 2 == 0 and s[:mid] == s[mid:]:
            res=""
            for i in range(0,mid):
                res=res+" "+s[i]
            return res
        return text

    def fix_garbled_text(self,text: str) -> str:
        """
        Detect if the text looks like every character is duplicated (e.g. 'RReeqquueesstt'),
        and if so, collapse it by taking every second character.
        Otherwise, return as is.
        """
        s = text.strip()
        if not s:
            return s

        # condition: even length and every pair is identical
        if len(s) % 2 == 0 and all(s[i] == s[i+1] for i in range(0, len(s), 2)):
            return s[::2]  # take every second char
        else:
            return s

    def fix_garbled_line(self,text: str) -> str:
        words = text.split()
        fixed_words = [self.fix_garbled_text(w) for w in words]
        return " ".join(fixed_words)

    def clean_text(self,text: str) -> str:
        # Fix garbled characters first
        fixed = self.fix_garbled_line(text)  # word-wise collapse
        # Then fix whole-line duplication
        fixed = self.remove_whole_line_duplication(fixed)
        return fixed
    
    def is_title(self,sentence, fontsCount, sentences_on_page1):
        """
        Classifies a sentence as title based on provided rules.
        Parameters:
            sentence (dict): sentence attributes, e.g. {'text': ..., 'top': ..., 'x0': ..., 'x1': ..., 'page': ..., 'font': ...}
            fontsCount (dict): {font_size: count_in_whole_doc}
            sentences_on_page1 (list): list of sentences (dicts) on page 1, each same as `sentence`
        Returns:
            True if sentence is title, else False
        """

        # Rule 1: On first page and has largest font
        largest_font = max(fontsCount.keys())
        if sentence['page'] == 1 and abs(sentence['font'] - largest_font) < 1e-2:
            # print("Title detected")
            return True

        # Rule 2: All fonts same size in the document
        if len(fontsCount) == 1:
            # Topmost sentence on first page is the title
            if sentences_on_page1:
                topmost_sentence = min(sentences_on_page1, key=lambda s: s['top'])
                if sentence is topmost_sentence or sentence['top'] == topmost_sentence['top']:
                    return True

        return False
    
    def determine_font_thresholds(self,lines):
        font_counts = defaultdict(int)
        font_pages = defaultdict(set)

        for line in lines:
            f = float(line['font'])
            p = int(line['page'])
            font_counts[f] += 1
            font_pages[f].add(p)

        # Sort fonts largest to smallest
        all_fonts = sorted(font_counts.keys(), reverse=True)

        # Filter out title font (largest font that appears only once on page 1)
        filtered_fonts = []
        for f in all_fonts:
            if font_pages[f] == {1}:
                # skip title font
                continue
            filtered_fonts.append(f)

        if not filtered_fonts:
            # fallback: use all_fonts if nothing remains
            filtered_fonts = all_fonts

        # pick thresholds
        h1_min_font = filtered_fonts[0] if len(filtered_fonts) > 0 else 14
        h2_min_font = filtered_fonts[1] if len(filtered_fonts) > 2 else h1_min_font - 2
        h3_min_font = filtered_fonts[2] if len(filtered_fonts) > 3 else h2_min_font - 2
        h4_min_font = filtered_fonts[3] if len(filtered_fonts) > 4 else h3_min_font - 2

        # print("All fonts (desc):", all_fonts)
        # print("Filtered fonts (desc):", filtered_fonts)
        # print("Using h1_min_font:", h1_min_font)
        # print("Using h2_min_font:", h2_min_font)
        # print("Using h3_min_font:", h3_min_font)
        # print("Using h4_min_font:", h4_min_font)

        return h1_min_font, h2_min_font, h3_min_font, h4_min_font

    def merge_lines(self,lines, x_tolerance=5, y_gap_tolerance=20):
        """
        Merge consecutive lines with same font and similar left padding.
        lines: list of dicts with keys ['text', 'font', 'x0', 'x1', 'top', 'page']
        Returns: merged list
        """
        if not lines:
            return []

        # Sort by page, then vertical position
        lines_sorted = sorted(lines, key=lambda l: (l['page'], l['top']))

        merged = []
        current = dict(lines_sorted[0])  # copy first line

        for next_line in lines_sorted[1:]:
            same_page = next_line['page'] == current['page']
            same_font = abs(float(next_line['font']) - float(current['font'])) < 0.1
            same_left = abs(float(next_line['x0']) - float(current['x0'])) <= x_tolerance
            same_bold = next_line['bold'] == current['bold']
            vertical_gap = float(next_line['top']) - float(current['top'])

            if next_line['text']!="" and same_bold and same_page and same_font and same_left and 0 < vertical_gap <= y_gap_tolerance:
                # merge
                current['text'] = current['text'].rstrip() + " " + next_line['text'].lstrip()
                # update rightmost x1 and top for group
                current['x1'] = max(current['x1'], next_line['x1'])
                current['top'] = next_line['top']  # keep bottom-most top for gap calc
            else:
                # push current and start new
                merged.append(current)
                current = dict(next_line)

        # push the last group
        merged.append(current)
        return merged
    
    def classify_headings(self, lines, page_width, h1_min_font, h2_min_font, h3_min_font, h4_min_font):
        if page_width is None:
            page_width = max(float(line['x1']) for line in lines if 'x1' in line)


        # Collect font size stats
        font_sizes = [float(line.get('font', 0)) for line in lines if line.get('text', '').strip()]
        most_common_font_size = max(set(font_sizes), key=font_sizes.count)

        # Count bolds
        # bold_count = sum(1 for line in lines if line['bold'])

        classified = []
        current_h1_font = None
        current_h2_font = None
        current_h3_font = None
        last_h3_x0 = None
        last_h4_x0 = None
        last_h1_x0 = None
        last_h2_x0 = None

        for line in lines:
            text = line.get('text', '').strip()
            font = float(line.get('font', 0))
            x0 = float(line.get('x0', 0))
            x1 = float(line.get('x1', 0))
            right_padding = page_width - x1
            is_line_bold = line['bold']

            if not text or text == self.title:
                classified.append({**line, "level": None})
                continue

            level = None

            # If font size is meaningful, apply normal logic
            if font != most_common_font_size:
                if h1_min_font and font >= h1_min_font and right_padding > 50:
                    level = "H1"
                    current_h1_font = font
                    last_h1_x0=x0
                    current_h2_font = None
                    current_h3_font = None
                    last_h3_x0 = None
                    last_h4_x0 = None
                    last_h2_x0 = None

                elif h2_min_font and current_h1_font and font < current_h1_font and font >= h2_min_font and right_padding > 50:
                    level = "H2"
                    current_h2_font = font
                    current_h3_font = None
                    last_h3_x0 = None
                    last_h4_x0 = None
                    last_h2_x0=x0

                elif h3_min_font and current_h2_font and font < current_h2_font and font >= h3_min_font and right_padding > 50:
                    if last_h3_x0 is None or abs(last_h3_x0 - x0) < 4:
                        level = "H3"
                        current_h3_font = font
                        last_h3_x0 = x0 if last_h3_x0 is None else min(x0, last_h3_x0)

                elif h4_min_font and current_h3_font and font < current_h3_font and font >= h4_min_font and right_padding > 50:
                    if last_h4_x0 is None or abs(last_h4_x0 - x0) < 4:
                        level = "H4"
                        last_h4_x0 = x0 if last_h4_x0 is None else min(x0, last_h4_x0)

            # Otherwise, fall back to bold-based classification
            elif is_line_bold and right_padding > 50:
                if (not current_h1_font or font==current_h1_font) and (not last_h1_x0 or abs(last_h1_x0-x0)<2):
                    level = "H1"
                    current_h1_font = font
                    last_h1_x0=x0
                    current_h2_font = None
                    current_h3_font = None
                    last_h3_x0 = None
                    last_h4_x0 = None
                    last_h2_x0 = None
                elif (not current_h2_font or font==current_h2_font) and (not last_h2_x0 or abs(last_h2_x0-x0)<2):
                    level = "H2"
                    current_h2_font = font
                    last_h2_x0=x0
                    current_h3_font = None
                    last_h3_x0 = None
                    last_h4_x0 = None
                elif not current_h3_font:
                    if last_h3_x0 is None or abs(last_h3_x0 - x0) < 4:
                        level = "H3"
                        current_h3_font = font
                        last_h3_x0 = x0
                else:
                    if last_h4_x0 is None or abs(last_h4_x0 - x0) < 4:
                        level = "H4"
                        last_h4_x0 = x0

            classified.append({**line, "level": level})

        return classified

    
    def is_bold(self,fontname):
        bold_keywords = ['bold', 'black', 'heavy', 'extrabold', 'semibold']
        return any(kw in fontname.lower() for kw in bold_keywords)

    def parseText(self,file_path,extract_whole_text=False):
        font_sizes = set()
        lines_by_page_and_size = defaultdict(lambda: defaultdict(list))

        self.title=""

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                chars_by_size = defaultdict(list)
                for char in page.chars:
                    fs = round(char["size"], 2)
                    chars_by_size[fs].append(char)
                    font_sizes.add(fs)
                    # print(char)
                    # break
                for fs, chars in chars_by_size.items():
                    # Sort to group by lines (top) and reading order (x0)
                    chars = sorted(chars, key=lambda c: (c["top"], c["x0"]))
                    lines = []
                    current_line = []
                    last_top = None
                    line_threshold = 2  # adjust for your PDF if needed

                    for char in chars:
                        isBold = False
                        if last_top is not None and abs(char["top"] - last_top) > line_threshold:
                            if current_line:
                                # Collect attributes for this line
                                line_top = current_line[0]["top"]
                                line_x0 = min(c["x0"] for c in current_line)
                                line_x1 = max(c["x1"] for c in current_line)
                                # Restore spaces between words
                                line_text = ""
                                prev_char = None
                                for c in current_line:
                                    if prev_char is not None:
                                        gap = c["x0"] - prev_char["x1"]
                                        if gap > 1.5:
                                            line_text += " "
                                    line_text += c["text"]
                                    prev_char = c
                                isBold = self.is_bold(current_line[0]["fontname"])
                                # if line_text.strip()!="":
                                lines.append({
                                    "text": line_text.strip(),
                                    "top": line_top,
                                    "x0": line_x0,
                                    "x1": line_x1,
                                    "page": page_num,
                                    "font": fs,
                                    "bold": isBold
                                })
                            current_line = []
                        current_line.append(char)
                        last_top = char["top"]
                    # Append the last line
                    if current_line:
                        line_top = current_line[0]["top"]
                        line_x0 = min(c["x0"] for c in current_line)
                        line_x1 = max(c["x1"] for c in current_line)
                        line_text = ""
                        prev_char = None
                        isBold = False
                        isBold = self.is_bold(current_line[0]["fontname"])
                        for c in current_line:
                            if prev_char is not None:
                                gap = c["x0"] - prev_char["x1"]
                                if gap > 1.5:
                                    line_text += " "
                            line_text += c["text"]
                            prev_char = c
                        # if line_text.strip()!="":
                        lines.append({
                            "text": line_text.strip(),
                            "top": line_top,
                            "x0": line_x0,
                            "x1": line_x1,
                            "page": page_num,
                            "font": fs,
                            "bold": isBold
                        })
                    lines_by_page_and_size[page_num][fs] = lines

        # Example output per page and font size
        # for page_num, sizes in lines_by_page_and_size.items():
            # print(f"\nPage {page_num}:")
        #     for fs, lines in sizes.items():
                # print(f"  Font size {fs}:")
        #         for line in lines:
                    # print(f"    {line}")

        sizes_count=dict()
        for s in font_sizes:
            sizes_count[s]=0
        for page_num, sizes in lines_by_page_and_size.items():
            for fs, lines in sizes.items():
                sizes_count[fs]+=len(sizes[fs])    

        # print(sizes_count)

        sentences_on_page1 = [
            {**line, "page": 1}
            for lines in lines_by_page_and_size[1].values()
            for line in lines
        ]

        # print(sentences_on_page1)

    

        # Usage example:
        # subtitle_sentence = find_subtitle(sentences_on_page1, fontsCount, title_sentence)
        # if subtitle_sentence:
            # print("Subtitle found:", subtitle_sentence['text'])
        # else:
            # print("No subtitle detected.")

        # print("\n\n")

        all_lines = [
            {**line, "page": page_num}
            for page_num, size_dict in lines_by_page_and_size.items()
            for lines in size_dict.values()
            for line in lines
        ]

        for sent in sentences_on_page1:
            if sent['text']!="" and self.is_title(sent,fontsCount=sizes_count,sentences_on_page1=sentences_on_page1):
                sent['level']='title'
                self.title=sent['text']
                # all_lines
                # print(sent)
                break

        merged = self.merge_lines(all_lines)
        # for l in merged:
            # print(l['text'])

        h1_min_font, h2_min_font, h3_min_font, h4_min_font = self.determine_font_thresholds(merged)



        # print("\n\n")
        result = self.classify_headings(merged, None, h1_min_font, h2_min_font, h3_min_font, h4_min_font)
        # for item in result:
        #     if item.get("level") is not None and item.get("level") in ["H1","H2","H3","H4"]:
                # print(f"Page {item['page']}, level {item['level']}: {item['text']}")

        # classified_lines = output from your classify_headings()
        # filter only those with a level

        outline = []
        special_heading_chars = {"•", "-", "*", "–", "—"}

        for idx, line in enumerate(result):
            level = line.get("level")
            text = self.clean_text(line.get("text", "").strip())
            page = line.get("page", 1) - 1

            is_heading = level in ("H1", "H2", "H3", "H4")
            is_symbol_heading = is_heading and text in special_heading_chars

            if is_heading and not is_symbol_heading:
                section = {
                    "level": level,
                    "text": text,
                    "page": page
                }

                if extract_whole_text:
                    collected = []
                    for next_line in result[idx + 1:]:
                        next_level = next_line.get("level")
                        next_text = self.clean_text(next_line.get("text", "").strip())
                        next_is_symbol = next_text in special_heading_chars
                        if next_level in ("H1", "H2", "H3", "H4") and not next_is_symbol:
                            break
                        collected.append(self.clean_text(next_line.get("text", "")))

                    section["content"] = "\n".join(collected)

                outline.append(section)

            elif is_symbol_heading and extract_whole_text and outline:
                # Merge content into previous section
                prev_section = outline[-1]
                symbol_content = line.get("content", "").strip()
                if symbol_content:
                    prev_section["content"] += f"\n{symbol_content}"


        pdf_json = {
            "title": self.clean_text(self.title),
            "outline": outline
        }

        # print(json.dumps(pdf_json, indent=2))
        return pdf_json

# file_path='/Users/viswa/Documents/adobe/adobe_hackathon/Adobe-India-Hackathon25/Challenge_1a/sample_dataset/pdfs/file03.pdf'
# file_path='/Users/viswa/Documents/adobe/adobe_hackathon/Adobe-India-Hackathon25/Challenge_1b/Collection 1/PDFs/South of France - Cuisine.pdf'
# temp = Task_1A()
# temp.parseText(file_path,True)
from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer, util
import datetime
from sentence_transformers import SentenceTransformer, util
from transformers import T5Tokenizer, T5ForConditionalGeneration
import json

all_sections = [
    {
        "document": "South of France - Cities.pdf",
        "section_title": "Comprehensive Guide to Major Cities in the South of France",
        "page": 1,
        "text": """The South of France is home to vibrant cities such as Nice, Marseille, and Cannes. 
Each city offers unique attractions, cultural experiences, and historical landmarks. 
Nice is known for its Promenade des Anglais and Mediterranean beaches. Marseille offers 
a rich maritime history and vibrant old port, while Cannes is famous for its film festival 
and luxury lifestyle."""
    },
    {
        "document": "South of France - Things to Do.pdf",
        "section_title": "Coastal Adventures",
        "page": 2,
        "text": """Explore the Mediterranean coastline through beach hopping, sailing tours, and scuba diving. 
Antibes and Saint-Tropez offer sandy beaches and lively nightlife, while the Calanques near Marseille 
are perfect for hiking and kayaking."""
    },
    {
        "document": "South of France - Cuisine.pdf",
        "section_title": "Culinary Experiences",
        "page": 6,
        "text": """Experience authentic French cuisine with cooking classes, wine tours, and local market visits. 
Learn to make bouillabaisse in Marseille, enjoy truffle hunting in Provence, and taste world-renowned 
rosé wines."""
    },
    {
        "document": "South of France - Tips and Tricks.pdf",
        "section_title": "General Packing Tips and Tricks",
        "page": 2,
        "text": """Pack layers to adapt to changing weather, use packing cubes to save space, and carry travel-sized 
toiletries. Don’t forget a universal adapter and copies of important documents."""
    },
    {
        "document": "South of France - Things to Do.pdf",
        "section_title": "Nightlife and Entertainment",
        "page": 11,
        "text": """Enjoy vibrant nightlife at Monaco’s jazz bars, Nice’s cocktail lounges, and Cannes’ luxury beach clubs. 
Saint-Tropez’s famous clubs offer live music and celebrity sightings."""
    },
    {
        "document": "South of France - History.pdf",
        "section_title": "Medieval Heritage",
        "page": 4,
        "text": """Discover medieval villages, castles, and cathedrals across the region. 
Carcassonne’s fortified walls and Avignon’s papal history are highlights."""
    }
]



# Your input
# all_sections = [ ... ]  # (paste your sample here)
class Task_1B():
    def __init__(self):
        self.embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # ~80MB
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.summarizer = T5ForConditionalGeneration.from_pretrained('t5-small')
        self.summarizer.to('cpu')  # ensure CPU
    
    # ========== Summarize top N ==========
    def summarize(self,text, max_input=512, max_output=120):
        inp = self.tokenizer("summarize: " + text, return_tensors="pt", max_length=max_input, truncation=True)
        out_ids = self.summarizer.generate(inp['input_ids'], max_length=max_output, min_length=40, length_penalty=2.0)
        return self.tokenizer.decode(out_ids[0], skip_special_tokens=True)

    def process_sections(self,all_sections,persona,job):
        # Rank sections
        query = f"{persona}. {job}"
        query_emb = self.embed_model.encode(query, convert_to_tensor=True)

        for sec in all_sections:
            title_emb = self.embed_model.encode(sec['section_title'], convert_to_tensor=True)
            sec['score'] = util.cos_sim(query_emb, title_emb).item()

        ranked = sorted(all_sections, key=lambda x: x['score'], reverse=True)

        top_n = 5
        extracted_sections = []
        subsection_analysis = []

        for rank, sec in enumerate(ranked[:top_n], start=1):
            summary = self.summarize(sec['text'])
            extracted_sections.append({
                "document": sec['document'],
                "section_title": sec['section_title'],
                "importance_rank": rank,
                "page_number": sec['page']
            })
            subsection_analysis.append({
                "document": sec['document'],
                "refined_text": summary,
                "page_number": sec['page']
            })

        # ========== Build final JSON ==========
        output = {
            "metadata": {
                "input_documents": list({sec['document'] for sec in all_sections}),
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.datetime.now().isoformat()
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }

        # Print or save
        # print(json.dumps(output, indent=4))
        return output


# persona = "Travel Planner"
# job = "Plan a trip of 4 days for a group of 10 college friends"

# node = Task_1B()
# node.process_sections(all_sections,persona,job)
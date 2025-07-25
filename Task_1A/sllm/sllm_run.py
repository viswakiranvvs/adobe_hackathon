from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer, util

# Load tiny models (CPU)
embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # ~80MB
tokenizer = T5Tokenizer.from_pretrained('t5-small')
summarizer = T5ForConditionalGeneration.from_pretrained('t5-small')  # ~220MB
summarizer.to('cpu')

# Step 1: rank sections
query = f"Travel Planner: Plan a trip of 4 days for a group of 10 college friends"
query_emb = embed_model.encode(query, convert_to_tensor=True)

# for sec in all_sections:
#     sec_emb = embed_model.encode(sec['section_title'], convert_to_tensor=True)
#     sec['score'] = util.cos_sim(query_emb, sec_emb).item()

# ranked = sorted(all_sections, key=lambda x: x['score'], reverse=True)[:5]

# Step 2: summarize
def summarize_text(text):
    inputs = tokenizer("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = summarizer.generate(inputs['input_ids'], max_length=150, min_length=40, length_penalty=2.0)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# for sec in ranked:
#     sec['refined_text'] = summarize_text(sec['text'])

# Build output JSON

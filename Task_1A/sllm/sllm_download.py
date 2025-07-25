from transformers import AutoTokenizer, AutoModel

model_name = "microsoft/layoutlmv3-base" 

save_dir = "./layoutlmv3_local"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

tokenizer.save_pretrained(save_dir)
model.save_pretrained(save_dir)

FROM python:3.11.13

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole challenge_1b folder
COPY . .

# Entrypoint
CMD ["python", "summarize_pdfs.py"]
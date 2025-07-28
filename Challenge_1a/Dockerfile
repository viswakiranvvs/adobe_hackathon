FROM python:3.11.13

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole challenge_1a folder
COPY . .

# Entrypoint
CMD ["python", "process_pdfs.py"]
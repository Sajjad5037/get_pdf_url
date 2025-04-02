from fastapi import FastAPI, File, UploadFile
from google.cloud import storage
import os

app = FastAPI()

# Configure your Google Cloud Storage Bucket
BUCKET_NAME = "your-bucket-name"

def upload_to_gcs(file, filename):
    """Uploads a file to Google Cloud Storage."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_file(file)
    blob.make_public()  # Make the file publicly accessible
    return blob.public_url

@app.post("/uploadPdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Handles PDF upload and returns the public URL."""
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are allowed"}

    pdf_url = upload_to_gcs(file.file, file.filename)
    return {"pdfUrl": pdf_url}

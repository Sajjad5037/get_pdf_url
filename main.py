import os
import base64
from google.cloud import storage
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sajjadalinoor.vercel.app"],  # Explicitly allow only your frontend
    allow_credentials=True,  # Allow cookies/auth headers if needed
    allow_methods=["GET", "POST", "OPTIONS"],  # Limit allowed methods
    allow_headers=["Content-Type", "Authorization"],  # Specify necessary headers
)
# Configure your Google Cloud Storage Bucket
BUCKET_NAME = "pdf_url"

# Decode the base64-encoded credentials from the environment variable and save it as a file
encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_BASE64")
if encoded_credentials:
    # Decode the credentials
    decoded_credentials = base64.b64decode(encoded_credentials)

    # Write the decoded content to a temporary file
    with open("google-credentials.json", "wb") as cred_file:
        cred_file.write(decoded_credentials)

    # Set the environment variable for Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-credentials.json"

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


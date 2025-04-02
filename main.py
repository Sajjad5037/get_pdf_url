import os
from google.cloud import storage
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
    print("Base64-encoded credentials found, decoding...")
    # Decode the credentials
    decoded_credentials = base64.b64decode(encoded_credentials)

    # Write the decoded content to a temporary file
    with open("google-credentials.json", "wb") as cred_file:
        cred_file.write(decoded_credentials)
    print("Google Cloud credentials saved to 'google-credentials.json'.")

    # Set the environment variable for Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-credentials.json"
    print("Environment variable GOOGLE_APPLICATION_CREDENTIALS set.")
else:
    print("No Google Cloud credentials found in environment variable.")

def upload_to_gcs(file, filename):
    """Uploads a file to Google Cloud Storage."""
    print(f"Uploading file {filename} to Google Cloud Storage...")

    try:
        # Initialize Google Cloud Storage client
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        
        # Upload the file directly from the UploadFile object to GCS
        blob.upload_from_file(file, content_type="application/pdf")
        blob.make_public()  # Make the file publicly accessible
        print(f"File {filename} uploaded successfully and made public.")
        
        # Return the public URL of the uploaded file
        return blob.public_url
    except Exception as e:
        print(f"Error uploading file to GCS: {e}")
        raise HTTPException(status_code=500, detail="Error uploading file to storage")

@app.post("/uploadPdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Handles PDF upload and returns the public URL."""
    print(f"Received request to upload file: {file.filename}")

    if not file.filename.endswith(".pdf"):
        print(f"Rejected file {file.filename}: Only PDF files are allowed.")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Print some details about the file
    print(f"File details - Filename: {file.filename}, Content Type: {file.content_type}")

    try:
        # Upload the PDF to Google Cloud Storage and get the URL
        pdf_url = upload_to_gcs(file.file, file.filename)
        print(f"Successfully uploaded PDF. Returning URL: {pdf_url}")
        return {"pdfUrl": pdf_url}
    except Exception as e:
        print(f"Error during file upload: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

if __name__ == "__main__":
    print("Starting FastAPI app...")
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

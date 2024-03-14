import functions_framework
from flask import jsonify, request
from google.cloud import storage

def upload_pdf(request):
  """Triggered by an HTTP POST request with a PDF file.

  Args:
      request (flask.Request): HTTP request object.

  Returns:
      flask.Response: JSON response with upload status.
  """

  bucket_name = "curlbrac-test-pdf"
  folder_path = "abc/"

  # Check if PDF file is present
  if 'file' not in request.files:
    return jsonify({"error": "No PDF file found in request"}), 400

  # Get the uploaded file
  pdf_file = request.files['file']

  # Validate file type (optional)
  if not pdf_file.filename.endswith('.pdf'):
    return jsonify({"error": "Invalid file format. Only PDF allowed"}), 400

  # Get filename and create unique name (optional)
  filename = pdf_file.filename
  # You can generate a unique filename here using libraries like uuid

  # Create a Storage client
  client = storage.Client()

  # Reference the object to upload (bucket name and filename)
  bucket = client.bucket(bucket_name)
  blob = bucket.blob(f'{folder_path}{filename}')

  # Upload the PDF file
  blob.upload_from_string(pdf_file.read())

  # Return success message
  return jsonify({"message": f"PDF file {filename} uploaded successfully!"}), 200


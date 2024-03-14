import os
from io import BytesIO

import functions_framework
import psycopg2
from flask import jsonify, request
from google.cloud import storage
from langchain.embeddings import VertexAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from PyPDF2 import PdfReader


def process_pdf(request):
  bucket_name = "curlbrac-test-pdf"
  folder_path = "abc"

  pdf_file = get_pdf(bucket_name,folder_path, "Design Ticketmaster.pdf")
  extracted_pdf_text = get_pdf_text(pdf_file)
  pdf_chunks = get_text_chunks(extracted_pdf_text)

  insert_embeddings(pdf_chunks)

  test_result = get_postgres_connect_str() # pdf_chunks #vector_db.connection_string
  

  # Return success message
  return jsonify({"message": f"Text = {test_result}"}), 200

def get_pdf(bucket_name, folder_path, file_name):
  # Create a Cloud Storage client
  storage_client = storage.Client()

  # Construct the full file path in Cloud Storage
  file_path = f"{folder_path}/{file_name}"

  try:
    # Download the file content as a byte string
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    file_content = blob.download_as_string()

    # Use BytesIO to simulate a file object
    pdf_file = BytesIO(file_content)
    return pdf_file

  except Exception as e:
    return f'Error extracting text from PDF - {file_name}: {str(e)}'

def get_pdf_text(pdf):
    text = ""
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
      text_without_nul = page.extract_text().replace("\x00", "")
      text+= text_without_nul
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200
    )
    chunks = text_splitter.split_text(text)
    doc_chunks = text_splitter.create_documents(chunks)
    return doc_chunks

def insert_embeddings(text_chunks):
    embeddings = VertexAIEmbeddings(requests_per_minute=60)
    project_id = os.environ.get("GCP_PROJECT", "cosmic-rarity-416918")
    region = os.environ.get('REGION', "us-east4")
    instance_name = "curlbrac"
    connection_name = f"{project_id}:{region}:{instance_name}"
    connection_string = PGVector.connection_string_from_db_params(                                                  
        driver = os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        user = os.environ.get("PGVECTOR_USER", "postgres"),                                      
        password = os.environ.get("PGVECTOR_PASSWORD", "curlbrac"),                                  
        host = os.environ.get("PGVECTOR_HOST", "0.0.0.0"),                                            
        port = os.environ.get("PGVECTOR_PORT", "5432"),                                          
        database = os.environ.get("PGVECTOR_DATABASE", "vector_db")                                       
    )
    COLLECTION_NAME = 'test_collection'
    pgvector = PGVector.from_documents(
            connection_string=connection_string,
            embedding=embeddings,
            documents=text_chunks,
            collection_name=COLLECTION_NAME,
        )

def get_postgres_connect_str():
    #connection_string = f"postgresql+pg8000://{user}:{password}@{connection_name}/{db_name}"
    project_id = os.environ.get("GCP_PROJECT", "cosmic-rarity-416918")
    region = os.environ.get('REGION', "us-east4")
    instance_name = "curlbrac"
    connection_name = f"{project_id}:{region}:{instance_name}"
    user_name = "curlbrac_user"
    password = "curlbrac_user"
    db_name = "vector_db"

    #postgresql+psycopg2://<username>:<password>@<instance_connection_name>/<database_name>
    #connection_string = f"postgresql+pg8000://{user_name}:{password}@{connection_name}/{db_name}"
    #connection_string = f"postgresql+psycopg2://{connection_name}:5432/{db_name} user={user_name} password={password}"
    #connection_string = f"postgresql+psycopg2://{user_name}:{password}@{connection_name}/{db_name}"
    #connection_string = f"postgresql+psycopg2://{user_name}:{password}@/{db_name}?host=/cloudsql/{connection_name}"
    connection_string = f"postgresql+psycopg2://{user_name}:{password}@127.0.0.1:5432/{db_name}"
    
 
    return connection_string
  
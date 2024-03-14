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


def move_file(bucket_name, file_path):
  client = storage.Client()
  bucket = client.bucket(bucket_name)
  destination_folder = "processed/"

  source_blob = bucket.blob(file_path)
  dest_blob_name = os.path.join(destination_folder, os.path.basename(file_path))
  destination_blob = bucket.blob(dest_blob_name)
  source_blob.move(destination_blob)
  print(f"Moved file: {file_path} to {dest_blob_name}")


def process_pdf(event, context):
  bucket_name = event['bucket']
  file_path = event['name']

  print(f"File received. Processing file: {file_path} in bucket {bucket_name}")
  pdf_file = get_pdf(bucket_name,file_path)
  print(f"Extracted pdf content as byte stream")

  extracted_pdf_text = get_pdf_text(pdf_file)
  print(f"Extracted pdf text")

  pdf_chunks = get_text_chunks(extracted_pdf_text)
  print(f"Extracted pdf chunks")

  insert_embeddings(pdf_chunks)
  print(f"Inserted embeddings in vector database")

  move_file(bucket_name, file_path)
  print(f"Moved the file to processed folder")

  print(f"Processing of the PDF file completed successfully.")



def get_pdf(bucket_name, file_path):
  # Create a Cloud Storage client
  storage_client = storage.Client()

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
    connection_string = PGVector.connection_string_from_db_params(                                                  
        driver = os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        user = os.environ.get("PGVECTOR_USER"),                                      
        password = os.environ.get("PGVECTOR_PASSWORD"),                                  
        host = os.environ.get("PGVECTOR_HOST"),                                            
        port = os.environ.get("PGVECTOR_PORT"),                                          
        database = os.environ.get("PGVECTOR_DATABASE")                                       
    )
    COLLECTION_NAME = 'test_collection'
    pgvector = PGVector.from_documents(
            connection_string=connection_string,
            embedding=embeddings,
            documents=text_chunks,
            collection_name=COLLECTION_NAME,
        )


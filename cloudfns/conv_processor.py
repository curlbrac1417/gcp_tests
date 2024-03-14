import os

import functions_framework
from flask import jsonify, request
from langchain.chains import RetrievalQA
from langchain.embeddings import VertexAIEmbeddings
from langchain.llms import VertexAI
from langchain.vectorstores.pgvector import PGVector


def get_embeddings_vector_db():
    embeddings = VertexAIEmbeddings(requests_per_minute=60)
    connection_string = PGVector.connection_string_from_db_params(                                                  
        driver = os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        user = os.environ.get("PGVECTOR_USER", "postgres"),                                      
        password = os.environ.get("PGVECTOR_PASSWORD", "curlbrac"),                                  
        host = os.environ.get("PGVECTOR_HOST", "0.0.0.0"),                                            
        port = os.environ.get("PGVECTOR_PORT", "5432"),                                          
        database = os.environ.get("PGVECTOR_DATABASE", "vector_db")                                       
    )
    COLLECTION_NAME = 'test_collection'

    db = PGVector.from_existing_index(
        embedding=embeddings,
        connection_string=connection_string,
        collection_name=COLLECTION_NAME,
    )
    return db


def conv_processor(request):

    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'prompt' in request_json:
        prompt = request_json['prompt']
    elif request_args and 'prompt' in request_args:
        prompt = request_args['prompt']
    else:
        return jsonify({"error": "No prompt in request"}), 400

    llm = VertexAI(
        model_name='text-bison@001',
        max_output_tokens=256,
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        verbose=True,
    )
 
    vector_db = get_embeddings_vector_db()
   
    retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k":2})

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True, verbose=True)
  
    result = qa({"query": prompt})
    
    return jsonify({"result": result["result"]}), 200


import os
import traceback
import numpy as np
import json
from flask import Flask, request, jsonify
from pinecone import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from boto3.dynamodb.conditions import Attr
from flask_cors import CORS  
from pypdf import PdfReader
import os
import re
import json
import boto3
import jwt
import datetime
import hashlib
from botocore.exceptions import ClientError
import requests
from openai import OpenAI
import uuid
from google.auth.transport.requests import Request
from google.oauth2.id_token import fetch_id_token
from together import Together
import vertexai
from vertexai.generative_models import GenerativeModel
from boto3.dynamodb.conditions import Key, Attr
from rouge import Rouge

# Ensure fallback for unsupported operations on MPS
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
PINECONE_KEY = os.getenv("PINECONE_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
TABLE_NAME = os.getenv("TABLE_NAME")
TOKEN = os.getenv("TOKEN")
LLAMA_URL = os.getenv("LLAMA_URL")
BACKEND_DOMAIN = os.getenv("BACKEND_DOMAIN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
SALT = "A VERY STRONG SALT"
SECRET="A VERY SECURE SECRET"
USER_TABLE_NAME = 'research_user_table'




# Initialize DynamoDB client for user DB
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

sqs = boto3.client(
    'sqs',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
# AWS_ACCESS_KEY_ID = "AKIA6ODU6VDBY2U5IAWS"  # Replace with your Access Key
# AWS_SECRET_ACCESS_KEY = "DRweNvCw0jtH3r46tGcvnwiZzB/2X2SQdTr6FN5p"  # Replace with your Secret Key
# Replace with your queue URL
QUEUE_URL = 'https://sqs.us-west-2.amazonaws.com/992382724291/UserEmailQueue'




pc = Pinecone(api_key=PINECONE_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

openAIClient = OpenAI(api_key=OPENAI_API_KEY,)
client = Together(api_key=TOGETHER_API_KEY)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route('/register', methods=['POST'])
def register():
    """
    API to accept email and password, and send the email to SQS.
    """
    try:
        # Parse request data
        data = request.json
        email = data.get('email')
        password = data.get('password')  # Currently not used, but should be validated

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        hashed_password = hashlib.sha256((password + SALT).encode('utf-8')).hexdigest()

        # Step 1: Send email ID to SQS
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({'email': email})
        )

        new_uuid = uuid.uuid4()

        # Step 2: Store user details in DynamoDB
        table = dynamodb.Table(USER_TABLE_NAME)
        dynamodb_response = table.put_item(
            Item={
                'email': email,
                'password': hashed_password,
                'paper_id': [],
                'active': 0,
                'user_id': str(new_uuid)
            }
        )

        return jsonify({
            'message': 'Email submitted successfully',
            'messageId': response['MessageId']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    """
    API to accept email and password, validate user details from DynamoDB, 
    and handle different cases such as non-existent user, invalid password, 
    or inactive account.
    """
    try:
        # Parse request data
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Access DynamoDB table
        table = dynamodb.Table(USER_TABLE_NAME)
        dynamodb_response = table.query(
            KeyConditionExpression=Key('email').eq(email)
        )

        # Check if the user exists
        if not dynamodb_response.get('Items'):
            return jsonify({'error': 'User does not exist'}), 404

        user_data = dynamodb_response['Items'][0]  # Assuming email is unique

        hashed_password = hashlib.sha256((password + SALT).encode('utf-8')).hexdigest()
        
        # Validate password
        if user_data.get('password') != hashed_password:  # Ensure proper hashing in production
            return jsonify({'error': 'Invalid password'}), 401

        # Check if the account is active
        if user_data.get('active') != 1:
            return jsonify({'error': 'Account not activated yet, please activate'}), 403

        payload = {
            'email': email,
            'uuid': user_data.get('user_id'),  # Assuming 'user_id' is the UUID
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token expires in 24 hours
        }
        token = jwt.encode(payload, SECRET, algorithm='HS256')

        # Successful login
        return jsonify({'message': 'Login successful', 'token': token}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Split text into manageable chunks
def split_text_with_langchain(text, chunk_size=4000, chunk_overlap=500):
    """
    Splits the text into manageable chunks using LangChain's RecursiveCharacterTextSplitter.
    Args:
        text (str): The text to split.
        chunk_size (int): Maximum size of each chunk in tokens.
        chunk_overlap (int): Number of overlapping characters between chunks.
    Returns:
        List of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks

def parse_pdf_to_text(pdf_file):
    """
    Extracts text from an uploaded PDF file.
    Args:
        pdf_file (FileStorage): The uploaded PDF file from the request.
    Returns:
        str: Extracted text from the PDF.
    """
    reader = PdfReader(pdf_file)
    number_of_pages = len(reader.pages)
    text = ""
    for i in range(number_of_pages):
        page = reader.pages[i]
        text += page.extract_text()
    return text

def clean_filename(filename):
    """
    Cleans special characters from the filename to make it filesystem-safe.
    Args:
        filename (str): Original filename.
    Returns:
        str: Cleaned filename.
    """
    return re.sub(r'[^A-Za-z0-9]', '_', os.path.splitext(filename)[0])

def save_text_to_temp_file(text, folder_path, original_filename):
    """
    Saves the extracted text to a temporary file in a given folder.
    Args:
        text (str): The extracted text from the PDF.
        folder_path (str): Path to the folder where the text file will be saved.
        original_filename (str): The original filename of the PDF file.
    Returns:
        str: Path to the saved text file.
    """
    os.makedirs(folder_path, exist_ok=True)
    cleaned_filename = clean_filename(original_filename)
    text_file_path = os.path.join(folder_path, f"{cleaned_filename}.txt")
    with open(text_file_path, "w", encoding="utf-8") as file:
        file.write(text)
    return text_file_path, cleaned_filename

def get_embedding(text, model="text-embedding-3-small"):
    embeddings = []
    for chunk in text: 
        try:
            chunk = chunk.page_content.replace("\n", " ")
            embeddings.append(openAIClient.embeddings.create(input = [chunk], model=model).data[0].embedding)
        except Exception as e:
            chunk = chunk.replace("\n", " ")
            embeddings.append(openAIClient.embeddings.create(input = [chunk], model=model).data[0].embedding)
    return embeddings

def query_pinecone(query, top_k=10, paper_id=None):
    query_embedding = get_embedding([query])
    
    # This will be called from the /notebook page with a paper id for querying
    # If paper_id is None, then we will query ALL the papers
    filter_condition = None
    if paper_id:
        filter_condition = {"paper_id": "paper_"+str(paper_id)} 

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter_condition
    )
    return results

def get_auth_token():
    auth_request = Request()
    target_audience = LLAMA_URL
    id_token = fetch_id_token(auth_request, target_audience)
    print(f"Getting auth token: {id_token}")
    return id_token

def generate_answer(query, matches, model_type):
    context = " ".join(
        [match.get("metadata", {}).get("chunk", "") for match in matches if "metadata" in match]
    )
    input_text = f"This is my question: {query}, please answer the question based on the following context: {context}\n\nDo not mention that you have been given context\n"

    print(input_text)

    if model_type == "llama3.2":
        auth_token = get_auth_token()
        print(f"Auth token: {auth_token}")
        headers = {
        "Authorization": f"Bearer {auth_token}", 
        "Content-Type": "application/json"}
        data = {
            "model": "llama3.2:3b",
            "prompt": input_text,
            "stream": False}
        print("generating answer")
        try:
            response = requests.post(LLAMA_URL, json=data, headers=headers)
        except Exception as e:
            print(f"Error: {e}")
        print("generation done")
    elif model_type == "llama3.3":
        responseAPI = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[
                {"role": "system", "content": "You are a helpful assistant for the conducting research that answers questions based on provided context. Don't mention anything about the context when answering"},
                {"role": "user", "content": input_text}
            ],
        stream=False)
        print("generating answer")
        response = responseAPI.choices[0].message.content
        print("generation done")
    elif model_type == "gemini1.5":
        vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
        model = GenerativeModel("gemini-1.5-flash-002")
        print("generating answer")
        responseAPI = model.generate_content(input_text)
        response = responseAPI.candidates[0].content.parts[0].text
        print("generation done")
    return response

def s3_upload(file):
    """
    Uploads a file to S3 and returns the public URL.
    """
    if file:
        try:
            # Ensure the temp directory exists
            temp_dir = "temp/"
            os.makedirs(temp_dir, exist_ok=True)

            temp_dir = "temp/"
            os.makedirs(temp_dir, exist_ok=True)

            # Save the uploaded file locally
            temp_file_path = os.path.join(temp_dir, file.filename)
            file.save(temp_file_path)  # Save the file locally

            # Upload the saved file to S3
            s3 = boto3.resource(
                "s3",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION,
            )
            
            s3.Bucket(AWS_STORAGE_BUCKET_NAME).upload_file(
                temp_file_path,  # Path of the file saved locally
                file.filename,  # S3 key (filename in the bucket)
            )

            # Generate the file's public URL
            file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file.filename}"

            # Clean up: Remove the temporary file
            os.remove(temp_file_path)

            print(f"File successfully uploaded to S3: {file_url}")
            return file_url
        except Exception as e:
            print(f"Error uploading file to S3: {e}")
            return ""
    return ""
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK"}), 200

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.json
        query_text = data['query']
        model_type = data.get('model', "llama3.2")
        paper_id = data.get("file_id", None)
        print(f"1: query text: {query_text}, model type:{model_type}")
        pinecone_results = query_pinecone(query_text, 10, paper_id)
        matches = pinecone_results.get("matches", [])
        if not matches:
            return jsonify({"answer": "No relevant matches found in the database."})
        
        paper_ids = list(set(int(match['id'].split("#")[0].split("_")[1]) for match in matches))[:5]
        dynamo_response = getPapersFromDynamo(paper_ids)
        print(f"2: Paper IDs: {paper_ids}")
        print(f"4: Dynamo Response :{dynamo_response}")

        if type(dynamo_response) == str:
            return jsonify({"error": "Failed to retrieve data from DynamoDB.", "details": dynamo_response}), 500
        
        answer = generate_answer(query_text, matches[:3], model_type)
        if model_type == "llama3.2":
            answer = json.loads(answer.text)
            return jsonify({"result": str(matches), "dynamo_data": dynamo_response, "answer": answer['response']})
        return jsonify({"result": str(matches), "dynamo_data": dynamo_response, "answer": answer})
    except Exception as e:
        print("exception raised")
        error_trace = traceback.format_exc()
        print(f"Error: {error_trace}")
        return jsonify({"error": str(e), "trace": error_trace}), 500

def get_last_paper_id():
    try:
        # Access the table
        table = dynamodb.Table(TABLE_NAME)

        # Scan the table to get all PaperIds
        response = table.scan(
            ProjectionExpression="PaperID"  # Only fetch the PaperID attribute
        )

        # Extract PaperID values from the scan result
        paper_ids = [item["PaperID"] for item in response.get("Items", [])]

        # Find the maximum PaperID, which represents the "last" one
        if paper_ids:
            last_paper_id = max(paper_ids)
            return last_paper_id
        else:
            return "No PaperID found in the table."

    except Exception as e:
        print(f"Error: {e}")
        return None

def batch_upsert(index, vectors, batch_size=100):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
    print("Uploaded successfully")

@app.route('/summarize', methods=['POST'])
def summarize():    

    """
    Summarizes the uploaded PDF file.
    Expects a PDF file to be uploaded as a POST request.
    """
    try:
        table = dynamodb.Table(TABLE_NAME)
        # Check if a file is uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        token = request.form.get("token", None)
        original_filename = file.filename
        
        get_eval = request.form.get('get_eval', 'false').lower() in ['true', '1', 't', 'y', 'yes']

        # Store in S3
        s3_link = s3_upload(file)

        # # Extract text from the PDF
        text = parse_pdf_to_text(file)

        # Optionally save the extracted text to a temporary file
        temp_folder = "/tmp/pdf_texts"  # Define a temporary folder for saving text files
        temp_file_path, file_text_name = save_text_to_temp_file(text, temp_folder, original_filename)
        
        # Get latest paper ID
        latest_paper_id = get_last_paper_id()
        new_paper_id = latest_paper_id + 1

        # chunk + embedding of new file
        chunks = split_text_with_langchain(text)
        embeddings = get_embedding(chunks)

        # Store in pinecone
        pinecone_chunks = []
        for i, value in enumerate(chunks):
            temp_dict = {}
            temp_dict["id"] = "paper_" + str(new_paper_id) + "#chunk_" + str(i)
            temp_dict["values"] = embeddings[i]                
            temp_dict["metadata"] = {"paper_id": "paper_"+str(new_paper_id), "chunk_id": "chunk_" + str(i), "chunk": chunks[i]}
            pinecone_chunks.append(temp_dict)

        batch_upsert(index, pinecone_chunks)

        # Store in dynamo
        data_to_add = {
            "PaperTxtName": file_text_name + ".txt", 
            "PaperID": int(new_paper_id),  
            "PaperLink": s3_link,
            "PaperPDFName": original_filename
        }

        table.put_item(Item=data_to_add)

        if token:
            userTable = dynamodb.Table(USER_TABLE_NAME)
            decoded_payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            user_uuid = decoded_payload.get('uuid')
            email = decoded_payload.get("email")

            try:
                # Update paperId by appending this to user from user table based on uuid
                response = userTable.get_item(Key={'email': email, 'user_id': user_uuid})
                if 'Item' not in response:
                    return {"error": "User not found"}, 404

                user_item = response['Item']

                # Append the new paper ID to the paper_id list
                existing_papers = user_item.get('paper_id', [])
                if not isinstance(existing_papers, list):
                    return {"error": "Invalid paper_id field. Expected a list."}, 400
                
                if new_paper_id in existing_papers:
                    return {"message": "Paper ID already exists in the user's list"}, 200
                
                updated_papers = existing_papers + [int(new_paper_id)]

                # Update the record in DynamoDB
                userTable.update_item(
                    Key={'email': email,  'user_id': user_uuid},
                    UpdateExpression="SET paper_id = :new_paper_list",
                    ExpressionAttributeValues={':new_paper_list': updated_papers},
                    ReturnValues="UPDATED_NEW"
                )
            except Exception as e:
                print("Error: ", e)

        query = "Summarize the content clearly and concisely with a maximum word limit of 300 words."

        # responseAPI = client.chat.completions.create(
        # model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        # messages=[
        #         {"role": "system", "content": "You are a helpful assistant for the conducting research that answers questions based on provided context. Don't mention anything about the context when answering"},
        #         {"role": "user", "content": text}
        #     ],
        # stream=False)
        # print("generating answer")
        # response = responseAPI.choices[0].message.content
        # print("generation done")

        vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
        model = GenerativeModel("gemini-1.5-flash-002")
        
        input_text = f"\nPaper: {text}\n\nProvide a detailed summary based on the given paper, Give plain text avoid markdown don't give any extra information out of the scope of the given paper.\n"

        print("generating answer")
        try:
            print("test")
            responseAPI = model.generate_content(input_text)
            response = responseAPI.candidates[0].content.parts[0].text
        except Exception as e:
            print(e)
            
        print("generation done")

        if get_eval:
            evaluation_scores = {}
            eval_input_text = f"\nPaper: {text}\n\nPlease give the Abstract, Introdution and the conclusion from the paper. Give those sections as is. Give plain text avoid markdown don't give any extra information out of the scope of the given paper.\n"
            responseAPI = model.generate_content(eval_input_text)
            labels = responseAPI.candidates[0].content.parts[0].text

            rouge = Rouge()
            rouge_scores = rouge.get_scores(response, labels, avg=True)
            evaluation_scores['rouge'] = rouge_scores
            return jsonify({"message": str(response), "Evalutation_metric": evaluation_scores}), 200
        return jsonify({"message": str(response)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/addToDynamo', methods=['POST'])
def addToDynamo():
    try:
        with open('pdf_metadata.json', 'r') as file:
            pdf_metadata = json.load(file)

        table = dynamodb.Table(TABLE_NAME)

        for cleaned_filename, metadata in pdf_metadata.items():
            data_to_add = {
                "PaperTxtName": cleaned_filename + ".txt", 
                "PaperID": metadata[0],  
                "PaperLink": metadata[1],
                "PaperPDFName": metadata[2]  
            }

            table.put_item(Item=data_to_add)

        return jsonify({"message": "All items added successfully!"}), 200


    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getFromDynamo', methods=['POST'])
def getFromDynamo():
    try:
        request_data = request.get_json()
        paper_ids = request_data.get("PaperIDs")
        results = getPapersFromDynamo(paper_ids)

        if type(results) == str:
            return jsonify({"error": "Failed to retrieve data from DynamoDB.", "details": results}), 500

        return jsonify({"data": results}), 200

    except Exception as e:
        print(f"2.5: Exception: {e}")
        return jsonify({"error": str(e)}), 500

def getPapersFromDynamo(paper_ids):
    try:
        print(f"2.1: Paper IDs: {paper_ids}")

        if not paper_ids or not isinstance(paper_ids, list):
            print(f"2.2: If statement")
            return "Invalid input. Please provide a list of PaperIDs."

        table = dynamodb.Table(TABLE_NAME)
        print(f"2.3: Table name: {table}")

        results = []
        for paper_id in paper_ids:
            response = table.scan(
                FilterExpression=Attr("PaperID").eq(paper_id)
            )

            if 'Items' in response and response['Items']:
                results.extend(response['Items'])
        print(f"2.4: Results: {results}")

        return results

    except Exception as e:
        print(f"2.5: Exception: {e}")
        return str(e)


@app.route('/getPapers', methods=['POST'])
def get_papers():
    try:
        data = request.get_json()
        token = data["token"]
        if token == None:
            return jsonify([]), 200
        decoded_payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        user_uuid = decoded_payload.get('uuid')

        if not user_uuid:
            return jsonify({"error": "UUID is required"}), 400

        table = dynamodb.Table(USER_TABLE_NAME)
        response = table.scan(
            FilterExpression="user_id = :uuid",
            ExpressionAttributeValues={":uuid": user_uuid}
        )

        if 'Items' not in response or not response['Items']:
            return jsonify([])  
        
        user_data = response['Items'][0]

        paper_ids = user_data.get("paper_id", [])

        if not paper_ids:
            return jsonify([])
        
        papers = []
        for ind, paper_id in enumerate(paper_ids):
            try:
                paper_table = dynamodb.Table(TABLE_NAME)
         
                paper_response = paper_table.scan(FilterExpression=Attr('PaperID').eq(int(paper_id)))
                
                if 'Items' in paper_response:
                    papers.append({
                        "id": paper_id,
                        "name": paper_response['Items'][0].get("PaperPDFName", f"Paper_{paper_id}.pdf"),
                        "type": paper_response['Items'][0].get("type", "pdf"),
                        # "metadata": paper_response['Item'].get("metadata", {})
                    })
            except ClientError as e:
                print(f"Error fetching paper {paper_id}: {e.response['Error']['Message']}")


        return jsonify(papers), 200

    except ClientError as e:
        print(f"ClientError: {e.response['Error']['Message']}")
        return jsonify({"error": "Error fetching data from DynamoDB"}), 500
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
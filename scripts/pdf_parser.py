import os
import re
import boto3
from pypdf import PdfReader
import json

# Load configuration from environment variables or a config file
AWS_ACCESS_KEY_ID = "AKIA6ODU6VDB2NXG2KVA"
AWS_SECRET_ACCESS_KEY = "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"
AWS_S3_REGION_NAME = "us-west-2"
AWS_STORAGE_BUCKET_NAME = "research-llm-pdfs"
MEDIA_ROOT = "/tmp"  # Temporary storage for processing files

# Global counter for paperID
paper_id_counter = 1

# Dictionary to store the cleaned_filename as key and [S3 link, paperID] as value
filename_metadata = {}

def s3_upload(file_path):
    """
    Uploads a file to S3 and returns the public URL. 
    """
    if file_path:
        try:
            s3 = boto3.resource(
                "s3",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_S3_REGION_NAME,
            )
            
            s3.Bucket(AWS_STORAGE_BUCKET_NAME).upload_file(
                file_path,
                file_path.split("/")[-1],  # Use only the filename for S3 key
            )
            
            file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{file_path.split('/')[-1]}"
            os.remove(file_path)

            return file_url
        except Exception as e:
            print(f"Error uploading file to S3: {e}")
            return ""
    return ""

def parse_pdf_2(pdf_path):
    reader = PdfReader(pdf_path)
    number_of_pages = len(reader.pages)
    text = ""
    for i in range(number_of_pages):
        page = reader.pages[i]
        text += page.extract_text()
    return text

def save_text_to_file(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)

def process_pdfs_in_folder(folder_path):
    paper_id_counter=1
    output_path = '/Users/shreyasnyu/Documents/projects/cloud/parsed3'
    os.makedirs(output_path, exist_ok=True)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            try:
                pdf_path = os.path.join(folder_path, filename)
                parsed_text = parse_pdf_2(pdf_path)

                # Clean special characters from filename
                cleaned_filename = re.sub(r'[^A-Za-z0-9]', '_', os.path.splitext(filename)[0])
                
                # Use the s3_upload function to upload the file and get the S3 URL
                # with open(pdf_path, 'rb') as file:
                    # file.name = filename  # Simulate a file object with a name attribute
                s3_url = s3_upload(pdf_path)

                if s3_url:
                    # Store the metadata
                    filename_metadata[cleaned_filename] = s3_url
                    paper_id_counter += 1
    
                # Save parsed text to file
                output_text_file = os.path.join(output_path, f"{cleaned_filename}.txt")
                save_text_to_file(parsed_text, output_text_file)
                print(f"Parsed text has been saved to {output_text_file}")
                print(f"Metadata for {cleaned_filename}: {filename_metadata[cleaned_filename]}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Usage
folder_path = '/Users/shreyasnyu/Documents/projects/cloud/dataset'
if os.path.exists(folder_path):
    process_pdfs_in_folder(folder_path)
    metadata_file_path = "/Users/shreyasnyu/Documents/projects/cloud/ResearchLLM/pdf_metadata3.json"  # Adjust the file name/path as needed
    try:
        with open(metadata_file_path, "w") as metadata_file:
            json.dump(filename_metadata, metadata_file, indent=4)  # Save with indentation for readability
        print(f"PDF metadata has been saved to {metadata_file_path}")
    except Exception as e:
        print(f"Error saving PDF metadata to file: {e}")
else:
    print(f"The folder path '{folder_path}' does not exist.")

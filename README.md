# Cloud Based Research Paper Summarization Tool
A cloud based research paper summarizer tool. The application has the following capabilities:
- Query through our 3000+ research paper dataset
- Query a particular research that is uploaded by the user
- Get summarizes of any paper that is uploaded


# User flow
A user can query our vast dataset as soon as they land on to our application. For every query they search, they would get the top 5 relevant papers as well, and they can download those papers for further reading. To use all the functionalities of our app, the user would need to create an account and verify their accounts. We have a pipeline set in place for this. On registration, the user would get an email to activate their account. Once the account is active, you're all done! 

Now, the user can login to our application, move to the Query page and upload the papers that they want to ask questions about. As soon as they upload a file, they would get the summary of the uploaded file and can ask any questions they have regarding the file. 


# Dataset
We pulled data using the ArXiv api. And you can find the dataset here:
https://drive.google.com/drive/folders/1YpaAFDAtIHom010s-dLQ3QglTxfkTA6X?usp=sharing

This has the raw pdfs as well as the parsed text files. 

# System Design
![image](https://github.com/user-attachments/assets/716b3004-3fbf-46e8-bdb4-fec4b3d62fbe)


# Databases
- Pinecone: This is our vector database in this app. It holds indexes for 3 chunk sizes: 2500, 4000 and 8000.
- Embedding Model: OpenAI's text-embedding-3-small with 1536 dimensions
- DynamoDB: We used DynamoDB to hold our User Data (inclduding the papers they have uploaded) as well as our Research Paper metadata such as the S3 link and the pdf name.   


# Large Language Models
- LLama3.2: We hosted this on GCP Cloud Run.
- LLmaa3.3: A hosted model that we used from Together.ai
- Gemini1.5: A hosted model that we used from VertexAI

# Application Video
[https://youtu.be/qambwG9ZCnY](https://youtu.be/qambwG9ZCnY)

# Application Screenshots: 

<img width="1707" alt="Query Page" src="https://github.com/user-attachments/assets/361891ca-a609-4aa7-8e6b-531285e56ba3" />
<img width="1707" alt="Search Page" src="https://github.com/user-attachments/assets/873aedae-bba6-429e-b4cf-50dd5597b2e1" />


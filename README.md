# Research-mate: Agentic RAG Platform
An AI-powered research platform that enables users to upload, search, and query document collections against selectable Large Language Models for grounded, context-aware analysis.

## Key Features
- **Intelligent Document Search**: Query through our 3000+ research paper dataset with advanced RAG capabilities
- **Multi-LLM Support**: Choose from Llama 3.2 8B, Llama 3.3 70B, and Gemini 1.5 Flash for optimal performance
- **Document Upload & Analysis**: Upload research papers and get AI-powered summaries and question-answering
- **High Performance RAG**: Engineered RAG engine achieving 95% Recall@10 using Anthropic AI's Contextual Retrieval research
- **Optimized Pipeline**: 7x speedup and 85% memory reduction through quantization techniques


# User flow
A user can query our vast dataset as soon as they land on to our application. For every query they search, they would get the top 5 relevant papers as well, and they can download those papers for further reading. To use all the functionalities of our app, the user would need to create an account and verify their accounts. We have a pipeline set in place for this. On registration, the user would get an email to activate their account. Once the account is active, you're all done! 

Now, the user can login to our application, move to the Query page and upload the papers that they want to ask questions about. As soon as they upload a file, they would get the summary of the uploaded file and can ask any questions they have regarding the file. 


# Dataset
We pulled data using the ArXiv api. And you can find the dataset here:
https://drive.google.com/drive/folders/1YpaAFDAtIHom010s-dLQ3QglTxfkTA6X?usp=sharing

This has the raw pdfs as well as the parsed text files. 

# System Design
![image](https://github.com/user-attachments/assets/716b3004-3fbf-46e8-bdb4-fec4b3d62fbe)


# Tech Stack
## Backend
- **Python**: Core backend development with FastAPI framework
- **PyTorch**: Deep learning framework for model inference and optimization
- **vLLM**: High-performance LLM serving with quantization optimizations
- **Docker**: Containerization for consistent deployment across environments

## Frontend
- **ReactJS**: Modern, responsive user interface
- **TypeScript**: Type-safe frontend development

## Cloud Infrastructure
- **Google Cloud Platform (GCP)**: Primary cloud hosting platform
- **GCP Cloud Run**: Serverless hosting for Llama 3.2 8B model
- **VertexAI**: Managed AI platform for Gemini 1.5 Flash integration

## Databases & Storage
- **Pinecone**: Vector database with indexes for multiple chunk sizes (2500, 4000, 8000)
- **DynamoDB**: User data and research paper metadata storage
- **Amazon S3**: Document storage and retrieval

## AI/ML Components
- **OpenAI Embeddings**: text-embedding-3-small (1536 dimensions) for semantic search
- **Contextual Retrieval**: Advanced RAG implementation based on Anthropic AI's research
- **Model Quantization**: Performance optimization reducing memory usage by 85%

## Large Language Models
- **Llama 3.2 8B**: Self-hosted on GCP Cloud Run with vLLM optimization for high-performance inference
- **Llama 3.3 70B**: Hosted model integrated via Together.ai for complex reasoning tasks
- **Gemini 1.5 Flash**: Google's latest model accessed through VertexAI for multimodal capabilities

# Performance & Architecture Highlights

## Advanced RAG Implementation
- **95% Recall@10**: Achieved through implementation of Anthropic AI's Contextual Retrieval research
- **Multi-Model Selection**: Users can choose optimal LLM based on their specific use case requirements
- **Contextual Search**: Advanced semantic search across 3000+ research papers with multiple chunking strategies

## Performance Optimizations
- **7x Speed Improvement**: Through comprehensive pipeline optimization and model quantization
- **85% Memory Reduction**: Achieved via advanced quantization techniques without compromising accuracy
- **Scalable Architecture**: Cloud-native design supporting concurrent users and large document collections

## System Architecture
- **Microservices Design**: Modular architecture with FastAPI backend and ReactJS frontend
- **Containerized Deployment**: Docker-based deployment ensuring consistency across environments
- **Multi-Cloud Integration**: Leveraging GCP, AWS, and third-party AI services for optimal performance

# Application Video
[https://youtu.be/qambwG9ZCnY](https://youtu.be/qambwG9ZCnY)

# Application Screenshots: 

<img width="1707" alt="Query Page" src="https://github.com/user-attachments/assets/361891ca-a609-4aa7-8e6b-531285e56ba3" />
<img width="1707" alt="Search Page" src="https://github.com/user-attachments/assets/873aedae-bba6-429e-b4cf-50dd5597b2e1" />


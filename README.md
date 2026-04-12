# Multimodal RAG System

This repository features a comprehensive Multimodal Retrieval-Augmented Generation (RAG) system built with **Streamlit**, **Ollama**, and **LangChain**. It is designed to ingest, index, and retrieve information from a wide variety of formats, including text, images, and audio/video files.

---

## 🏗️ Architecture Design

The system implements a modular architecture to ensure high precision in multimodal information processing:

1.  **Multimodal Ingestion Pipeline**:
    * **Text & Documents**: Parses `.pdf`, `.docx`, `.pptx`, and `.txt` files using specialized loaders.
    * **Vision Processing**: Utilizes **Tesseract OCR** for text extraction and **LLaVA** models to generate descriptive captions for images, ensuring visual context is searchable.
    * **Speech-to-Text**: Employs **OpenAI Whisper** to transcribe `.mp3` and `.mp4` files into text documents.
2.  **Vector Management & Indexing**:
    * Documents are processed via a `RecursiveCharacterTextSplitter` to create chunks with metadata tracking.
    * Uses **Ollama Embeddings** and **FAISS** for efficient local vector storage and similarity search.
3.  **Refined Retrieval**:
    * Implements a two-stage retrieval process: initial vector similarity search followed by a semantic reranking stage to maximize accuracy.

---

## 🌟 Technical Highlights

### Advanced RAG Techniques
* **Semantic Reranking**: Enhances precision by re-evaluating the top-k candidate chunks using the `BAAI/bge-reranker-v2-m3` model.
* **Parent Document Retrieval (PDR) Concepts**: The system tracks `source` and `chunk_id` metadata, allowing the generator to maintain the relationship between specific fragments and their original documents for better context preservation.
* **MMR (Maximal Marginal Relevance)**: Includes configuration for diverse search methods to reduce redundancy in retrieved information.

### Multimodal Capabilities
* **Comprehensive File Support**: Handles unstructured data across images and audio/video by converting them into text-based semantic representations before indexing.
* **Local Inference**: Leverages **Ollama** to run both LLMs (e.g., LLaVA, GPT-OSS) and Embedding models locally, ensuring data privacy and offline capability.

---

## 🚀 Quick Start

### 1. Installation
Install the necessary Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Running the Application
Start the Streamlit interface:
```bash
streamlit run app.py
```
*Note: If using a conda environment, you may need to use `python -m streamlit run app.py`.*

### 3. Docker Deployment
To run the system in a containerized environment:
```bash
# Build and start the services
docker-compose up --build

# Access the UI at:
# http://140.113.24.231:8502
```
To shut down the services:
```bash
docker-compose down
```

---

## 📂 Project Components
* `Upload_file.py`: Multimodal data extraction (OCR, LLaVA, Whisper).
* `RAG_Embedding.py`: Vector database management and document chunking.
* `reranking.py`: Implementation of the BGE-reranker logic.
* `app.py`: Streamlit dashboard and model configuration.
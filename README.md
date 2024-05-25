# README

## Project: Talk to Your Data

This project allows users to interact with their data using Retrieval-Augmented Generation (RAG) techniques powered by LangChain, Milvus, and SentenceTransformers. By using this setup, users can query their documents and receive intelligent responses based on the content of their data.

### Key Components

1. **LangChain**: Provides the foundational framework for building conversational AI applications.
2. **Milvus**: An open-source vector database for storing and managing large-scale embeddings.
3. **SentenceTransformers**: Used for generating embeddings from text for efficient and accurate retrieval.

### Features

- **Conversation Management**: Uses `ConversationBufferMemory` to store and manage conversation history.
- **Document Embedding and Storage**: Converts documents into embeddings and stores them in Milvus for quick retrieval.
- **Real-time File Monitoring**: Detects changes in documents and updates the embeddings in the database accordingly.
- **FastAPI Integration**: Provides an API endpoint to interact with the system and retrieve answers based on user queries.

### Setup Instructions

#### Prerequisites

- Python 3.8+
- Docker (for running Milvus)

#### Installation

1. **Clone the Repository**:

```sh
git clone <repository_url>
cd <repository_directory>
```

2. **Set Up Environment Variables**:

Create a `.env` file in the root directory and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key
```

3. **Install Dependencies**:

```sh
pip install -r requirements.txt
```

4. **Run Milvus**:

Pull and run Milvus using Docker:

```sh
docker pull milvusdb/milvus
docker run -d --name milvus -p 19530:19530 milvusdb/milvus:latest
```

5. **Run the Application**:

```sh
python main.py
```

### Project Structure

- **main.py**: Main script to run the application.
- **index.py**: Using langchain reply back responses.
- **api.py**: FastAPI integration to provide an endpoint for querying.
- **templates/**: Directory containing prompt templates.
- **Files/**: Directory where documents to be indexed are stored.

### How It Works

1. **Initialization**:
   - Connects to Milvus and checks for the existence of the necessary collections.
   - If collections do not exist, they are created.

2. **Document Processing**:
   - Reads `.docx` files from the `Files` directory.
   - Converts document content into embeddings using SentenceTransformers.
   - Inserts the embeddings into Milvus.

3. **Real-time Monitoring**:
   - Monitors the `Files` directory for any changes in the documents.
   - Updates the embeddings in Milvus if any document is modified.

4. **Query Handling**:
   - Provides an endpoint via FastAPI to accept user queries.
   - Uses LangChain's `RetrievalQA` chain to retrieve and generate answers based on the indexed documents.

### Usage

- **Start the Application**:
  Ensure Milvus is running and then execute:

  ```sh
  python main.py
  ```

- **Query the System**:
  Use the provided API endpoint to query the system:

  ```sh
  curl -X GET "http://localhost:8000/get_answers?query=Your+query+here"
  ```

### Future Enhancements

- Support for more document formats.
- Advanced query capabilities with more sophisticated natural language understanding.
- Enhanced monitoring for more efficient updates to the database.

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Feel free to customize this README further based on your specific needs and project structure.

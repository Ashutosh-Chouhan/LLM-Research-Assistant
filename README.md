# LLM Research Assistant

A Retrieval-Augmented Generation (RAG) application that allows users to upload a research paper in PDF format and ask questions based on its content.

Instead of relying solely on the LLM's internal knowledge, the application retrieves relevant information directly from the uploaded document and uses it as context to generate grounded answers. Each answer also includes the relevant page number as a citation.

**Tech Stack:** Python · LangChain · Google Gemini · ChromaDB · Streamlit

---

## How It Works

```text
PDF
 └─> load_pdf()               Extract pages           (src/loader.py)
      └─> split_documents()   Create smaller chunks  (src/splitter.py)
           └─> embeddings     Text → vectors         (src/vectorstore.py)
                └─> ChromaDB  Store vectors          (vector_db/)

User Question
 └─> similarity_search()      Retrieve relevant chunks (src/rag.py)
      └─> prompt              Context + question       (src/prompts.py)
           └─> Gemini         Generate answer + citations
```

The complete PDF is not sent to the LLM for every question because of context-window limitations and unnecessary token usage.

Instead, the document is divided into smaller chunks and converted into vector embeddings. For each question, the application retrieves only the top-k most relevant chunks and sends them to Gemini as context.

This approach improves retrieval efficiency, reduces unnecessary token usage, and helps keep the generated answers grounded in the uploaded document.

---

## Key Features

* Upload research papers in PDF format
* Extract document text while preserving page information
* Split documents into smaller chunks
* Generate vector embeddings using Google Gemini
* Store embeddings using ChromaDB
* Perform semantic similarity search
* Generate document-grounded answers using Gemini
* Provide page-level citations with answers
* Reduce hallucinations using controlled prompting
* Streamlit-based interactive user interface
* Configurable chunk size, overlap, top-k retrieval, models, and temperature
* CLI-based PDF ingestion support

---

## Setup

### 1. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

---

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

### 3. Configure the Gemini API Key

This project uses the Google Gemini API for embeddings and answer generation.

Get your Gemini API key from:

https://aistudio.google.com/apikey

#### Create a `.env` File

In the **project root directory**, create a file named:

```text
.env
```

Your project structure should look like:

```text
LLM-Research-Assistant/
│
├── app.py
├── ingest.py
├── requirements.txt
├── .env
└── src/
```

Add your API key to the `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace `your_gemini_api_key_here` with your actual Gemini API key.

### Important Security Note

**Never hard-code your API key directly inside Python source code.**

Do not do this:

```python
GEMINI_API_KEY = "your_actual_api_key"
```

Instead, store the key in `.env` and load it through environment variables.

### Never Upload `.env` to GitHub

Your `.env` file contains sensitive credentials and **must not be committed to GitHub**.

Add the following to your `.gitignore` file:

```gitignore
.env
venv/
__pycache__/
*.pyc
vector_db/
```

If an API key is accidentally exposed on GitHub or shared publicly, revoke the exposed key immediately and generate a new one.

---

## Running the Application

### Option A — Streamlit Application

This is the recommended way to use the application.

```bash
streamlit run app.py
```

The Streamlit application will open in your browser.

Then:

1. Upload a research paper in PDF format.
2. Click **Process PDF**.
3. Wait for the document to be processed and indexed.
4. Ask questions about the uploaded paper.
5. The application retrieves relevant sections and generates an answer with page citations.

---

### Option B — Create the Vector Index Using CLI

To index all PDFs inside the `data/` directory:

```bash
python ingest.py
```

To index a specific PDF:

```bash
python ingest.py data/paper.pdf
```

After creating the vector index, start the application:

```bash
streamlit run app.py
```

---

### Test the PDF Loader

To test the PDF loading functionality:

```bash
python test_loader.py
```

---

## Project Structure

| File / Directory     | Description                                                                  |
| -------------------- | ---------------------------------------------------------------------------- |
| `app.py`             | Streamlit UI for PDF upload, chat, sources, and summaries                    |
| `ingest.py`          | CLI script for creating the vector index from PDFs                           |
| `list_models.py`     | Lists available Gemini models                                                |
| `test_loader.py`     | Tests the PDF loading functionality                                          |
| `src/config.py`      | Configuration for models, chunk size, top-k, temperature, and other settings |
| `src/loader.py`      | Loads PDFs and extracts pages as Document objects                            |
| `src/splitter.py`    | Splits documents into smaller text chunks                                    |
| `src/vectorstore.py` | Generates embeddings and saves/loads the ChromaDB vector store               |
| `src/rag.py`         | Retrieves relevant chunks and generates answers using Gemini                 |
| `src/prompts.py`     | Contains system prompts and anti-hallucination instructions                  |
| `data/`              | Directory for input research papers                                          |
| `vector_db/`         | Auto-generated ChromaDB vector index                                         |
| `.env`               | Stores the Gemini API key locally; should never be committed                 |

---

## RAG Pipeline

The application follows a Retrieval-Augmented Generation pipeline:

```text
                    ┌─────────────────┐
                    │   Research PDF  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   PDF Loader    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Chunking     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Embeddings    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    ChromaDB     │
                    └────────┬────────┘
                             │
                             │
User Question ───────────────┤
                             ▼
                    ┌─────────────────┐
                    │ Similarity      │
                    │ Search          │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Relevant Chunks │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Gemini LLM      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Answer + Page   │
                    │ Citations       │
                    └─────────────────┘
```

---

## Configuration and Tuning

Most RAG settings can be configured in:

```text
src/config.py
```

| Setting            |                       Default | Description                                                                                                        |
| ------------------ | ----------------------------: | ------------------------------------------------------------------------------------------------------------------ |
| `CHUNK_SIZE`       |                        `1000` | Size of each text chunk. Larger chunks provide more context but may reduce retrieval precision.                    |
| `CHUNK_OVERLAP`    |                         `200` | Number of overlapping characters/tokens between consecutive chunks to reduce information loss at chunk boundaries. |
| `TOP_K`            |                           `4` | Number of most relevant chunks retrieved for each question.                                                        |
| `TEMPERATURE`      |                         `0.1` | Controls the randomness of generated responses. Lower values generally favor more deterministic answers.           |
| `CHAT_MODEL`       |            `gemini-3.6-flash` | Gemini model used for generating answers.                                                                          |
| `EMBEDDING_MODEL`  | `models/gemini-embedding-001` | Model used to generate vector embeddings.                                                                          |
| `EMBED_BATCH_SIZE` |                          `40` | Number of texts processed in one embedding batch.                                                                  |

> **Note:** Model availability can change over time. If a configured Gemini model is no longer available, use `list_models.py` to check the currently available models and update `src/config.py`.

### Changing the Embedding Model

If you change:

```text
EMBEDDING_MODEL
```

you should rebuild the vector database:

```bash
python ingest.py
```

This is necessary because embeddings generated by different models may not be compatible.

---

## Troubleshooting

### `404 Model Not Found`

Google may retire, rename, or change the availability of models.

Run:

```bash
python list_models.py
```

Check the available models and update the model name in:

```text
src/config.py
```

---

### `429 RESOURCE_EXHAUSTED`

This usually indicates that an API rate limit or quota has been reached.

Possible solutions:

* Reduce `EMBED_BATCH_SIZE`
* Increase `EMBED_SLEEP_SECONDS`
* Wait and retry
* Check your Gemini API quota
* Use an appropriate API/model tier

---

### `GEMINI_API_KEY Not Found`

Make sure the `.env` file exists in the project root:

```text
LLM-Research-Assistant/
├── .env
├── app.py
└── src/
```

The `.env` file should contain:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Make sure:

* The file is named exactly `.env`
* It is located in the project root
* The variable name is exactly `GEMINI_API_KEY`
* The API key is valid
* `.env` has not been accidentally renamed to `.env.txt`

For comments inside `.env`, use `#`:

```env
# Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

Do not use `//` for comments.

---

### `Import "streamlit" could not be resolved`

VS Code may be using the wrong Python interpreter.

Open the Command Palette:

```text
Ctrl + Shift + P
```

Select:

```text
Python: Select Interpreter
```

Then choose:

```text
.\venv\Scripts\python.exe
```

---

## Security

This project uses an external LLM API and therefore requires an API key.

Keep the following information private:

* Gemini API keys
* Authentication tokens
* Environment variables containing secrets
* Private research papers
* Credentials and other sensitive configuration values

### Recommended `.gitignore`

```gitignore
# Environment variables
.env

# Virtual environment
venv/

# Python cache
__pycache__/
*.pyc

# Generated vector database
vector_db/

# Local research documents
data/

# VS Code settings
.vscode/
```

Never commit API keys, `.env` files, private documents, or other credentials to a public repository.

If a credential is accidentally exposed, revoke it immediately and create a new one.

---

## Future Improvements

The following features can be added in future versions:

* **Multi-PDF Support** — Upload and search across multiple research papers.
* **Conversation Memory** — Support contextual follow-up questions such as "What does this mean?"
* **Hybrid Search** — Combine keyword-based BM25 search with vector similarity search.
* **Reranker** — Re-rank retrieved chunks and select the most relevant results before sending them to the LLM.
* **Evaluation Pipeline** — Create a question-answer test set and evaluate retrieval and answer quality.
* **Source Highlighting** — Highlight the exact text passages used to generate an answer.
* **Document Summarization** — Generate structured summaries of research papers.
* **Metadata Filtering** — Filter retrieval results by paper, page, section, or other metadata.

---

## License

Copyright © 2026 Ashutosh Chouhan. All Rights Reserved.

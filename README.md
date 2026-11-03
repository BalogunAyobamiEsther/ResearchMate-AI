
# ResearchMate AI

An AI-powered academic research assistant that allows users to upload research papers, ask questions about their documents, and receive evidence-based answers with source and page citations.

## Features

- **PDF Upload:** Upload academic research papers in PDF format (maximum 20 MB).
- **Document Management:** View uploaded documents, inspect document details, and delete documents.
- **Intelligent Research Assistant:** Ask natural-language questions about uploaded research papers.
- **Retrieval-Augmented Generation (RAG):** Retrieve relevant passages from uploaded documents to ground AI-generated answers.
- **Evidence-Based Responses:** Generate answers using retrieved research passages.
- **Source Citations:** Display source IDs, document filenames, and page numbers.
- **Citation Validation:** Validate generated citations against retrieved sources.
- **Evidence Inspection:** Expand retrieved passages to examine supporting evidence.
- **PDF Page Navigation:** Open the original PDF directly from a citation at the cited page.
- **Insufficient Evidence Detection:** Identify questions that cannot be adequately answered from available passages.
- **Persistent Storage:** Store document embeddings in ChromaDB and retain original uploaded PDFs locally.

## Technology Stack

### Backend
- Python
- FastAPI
- PyMuPDF
- Sentence Transformers
- ChromaDB
- Google Gemini API
- Pydantic

### Frontend
- React
- JavaScript
- Vite
- CSS

## System Architecture

ResearchMate AI follows a Retrieval-Augmented Generation architecture.

1. A user uploads an academic PDF.
2. The backend extracts text and page information from the document.
3. Extracted text is divided into overlapping chunks.
4. Sentence Transformers generates vector embeddings.
5. Chunks and embeddings are stored in ChromaDB.
6. A user submits a research question.
7. The question is converted into an embedding.
8. ChromaDB retrieves relevant research passages.
9. Retrieved passages are supplied to Google Gemini.
10. Gemini generates an evidence-based response.
11. ResearchMate validates citations and returns the answer, citations, and supporting passages.
12. Users can open the original PDF at the cited page.

## Project Structure

```text
ResearchMate-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── schemas/
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── chunker.py
│   │   │   ├── embedding_service.py
│   │   │   ├── ingestion_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── pdf_processor.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── rag_service.py
│   │   │   ├── retrieval_service.py
│   │   │   └── vector_store.py
│   │   └── main.py
│   ├── storage/
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── documentService.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   └── package.json
│
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/BalogunAyobamiEsther/ResearchMate-AI.git
cd ResearchMate-AI
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

Add your Google Gemini API key:

```env
GOOGLE_GEMINI_TOKEN=your_google_gemini_api_key
```

Use your own valid API key. Never commit your `.env` file or expose API credentials publicly.

### 5. Start the backend

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend at:

```text
http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/documents/upload` | Upload and process a PDF |
| GET | `/api/v1/documents` | Retrieve uploaded documents |
| GET | `/api/v1/documents/{document_id}` | Retrieve document details |
| GET | `/api/v1/documents/{document_id}/file` | Retrieve original PDF |
| DELETE | `/api/v1/documents/{document_id}` | Delete a document |
| POST | `/api/v1/chat/query` | Submit a research question |
| GET | `/api/v1/health` | Check backend health |

## Running Tests

Run backend tests from the project root:

```bash
python -m pytest backend/tests/ -v
```

Current test status: **31 tests passed**.

## Production Build

Build the frontend:

```bash
cd frontend
npm run build
```

## Current Limitations and Future Improvements

- Research conversation history is not yet persisted.
- Document-scoped retrieval is not yet implemented.
- The current application is designed for local development and requires deployment before public access.
- Additional evaluation of retrieval quality and answer accuracy is needed.

Potential future improvements include:
- Persistent research conversation history.
- Selecting specific documents for question answering.
- User authentication and individual workspaces.
- Cloud deployment and scalable document storage.
- Advanced retrieval strategies and RAG evaluation.
- More comprehensive automated integration tests.

## Author

**Esther Balogun**

GitHub: [BalogunAyobamiEsther](https://github.com/BalogunAyobamiEsther)

---

ResearchMate AI — Making academic research easier through artificial intelligence.

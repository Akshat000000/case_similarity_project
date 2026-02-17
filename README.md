# ⚖️ Legex: AI-Powered Legal Case Similarity System

A semantic search and knowledge graph visualization platform for judicial records. This system allows legal professionals to find relevant case precedents using natural language queries and visualize relationships between cases with explainable ranking.

## 🚀 Key Features

*   **🔍 AI-Powered Semantic Search**: Multi-stage retrieval using `all-MiniLM-L6-v2` embeddings and `Cross-Encoder` reranking (MS-MARCO).
*   **📖 Case Explorer**: Browse sampled judicial records with automated keyword highlighting and text previews.
*   **🕸️ Similarity Graph**: Interactive visual network of case relationships built with Pyvis, allowing for structural analysis of precedents.
*   **⚖️ Explainable Ranking**: Transparent score breakdown (Embedding Similarity, Cross-Encoder relevance, Decision Outcome, and Reasoning availability).
*   **🧠 Expert Reasoning**: Extracts and displays curated reasoning/expert summaries from dataset metadata.
*   **🖍️ Dynamic Highlighting**: Automatically identifies and highlights significant query terms in the full judgment text.
*   **⚡ FastAPI Backend**: Decoupled architecture separating heavy AI processing from the Streamlit frontend.

## 📂 Project Structure

```
case_similarity_project/
├── api/                   # FastAPI Backend Server (Search & Retrieval)
├── data/                  # Dataset loading scripts (CJPE Dataset)
├── database/              # PostgreSQL schema & data ingestion logic
├── embeddings/            # Logic for generating and storing case embeddings
├── rerank/                # Cross-Encoder reranking implementation
├── search/                # Retrieval pipeline (Semantic Search + Ranking)
├── ui/                    # Streamlit Frontend Application
│   ├── Home.py            # Welcome Page
│   ├── api_client.py      # Backend API Integration
│   └── pages/             # App views (Case Explorer, Search + Graph)
├── utils/                 # Text preprocessing & highlighting utilities
├── .env                   # Environment/secrets (Postgres, Neo4j, Gemini)
└── requirements.txt       # Python dependencies
```

## 🛠️ Prerequisites

1.  **Python 3.10+**
2.  **PostgreSQL**: For storing structured case data and embeddings.
3.  **Neo4j**: Optional (for future knowledge graph expansion).

## ⚙️ Configuration

1.  **Clone the repository**.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables**:
    Create a `.env` file in the project root:
    ```env
    # Database Credentials
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=case_similarity_db
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=your-password

    # AI Model Keys (Optional)
    GEMINI_API_KEY=your-gemini-key
    ```

## 🏃 Usage

### 1. Ingest Data
Populate your local PostgreSQL database with the full CJPE dataset:
```bash
python -m database.ingest_full_dataset
```

### 2. Start the Backend API
The UI communicates with this API for all search operations:
```bash
uvicorn api.main:app --reload
```
*   API: `http://localhost:8000`
*   Docs: `http://localhost:8000/docs`

### 3. Launch the UI
Start the Streamlit application:
```bash
streamlit run ui/Home.py
```
*   Accessible at `http://localhost:8501`

## 🖥️ UI Modules

*   **📚 Case Explorer**: Randomly browse cases, read full judgments, and explore similar precedents directly from the database.
*   **🔍 Case Search**: Natural language search interface with "List" and "Graph" views.
*   **📊 Explained Ranking**: Interactive bar charts showing why each case was ranked for your specific query.
*   **🕸️ Graph View**: Dynamic relationship mesh of search candidates with interactive tooltips and case inspection.

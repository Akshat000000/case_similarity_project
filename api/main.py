from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
import contextlib

# Add project root to path so we can import modules
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from search.search_pipeline import CaseSearchPipeline
from database.db_connection import DatabaseConnection

# -----------------------------------------------------------------------------
# Global State (Model Loading)
# -----------------------------------------------------------------------------
# We store the pipeline globally so we load models only once on startup
pipeline_instance: Optional[CaseSearchPipeline] = None

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline_instance
    print("Loading AI Search Pipeline...")
    pipeline_instance = CaseSearchPipeline()
    print("Search Pipeline Loaded.")
    yield
    # Clean up if needed
    pipeline_instance = None

app = FastAPI(title="Case Similarity API", lifespan=lifespan)

# -----------------------------------------------------------------------------
# Pydantic Models
# -----------------------------------------------------------------------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5 

class CaseData(BaseModel):
    case_id: str
    text: Optional[str] = None
    summary: Optional[str] = None
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    embed_score: Optional[float] = None
    final_score: Optional[float] = None
    # Flexible dict for other fields like score_breakdown
    extra_data: Optional[Dict[str, Any]] = None

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Case Similarity API is running"}

@app.post("/search", response_model=List[Dict[str, Any]])
def search_cases(request: SearchRequest):
    """
    Search for similar cases using the semantic search pipeline.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty")
    
    if pipeline_instance is None:
        raise HTTPException(status_code=503, detail="Search service not initialized")

    try:
        # Note: The search method currently returns top 5 hardcoded in the pipeline file we saw earlier,
        # or we might need to adjust the pipeline to accept top_k.
        # Looking at previous view_file, pipeline.search(query) calls retrieve(top_k=10) and rerank(top_k=10) then returns [:5]
        # We will just call search for now.
        results = pipeline_instance.search(request.query)
        return results
    except Exception as e:
        print(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cases/random", response_model=List[Dict[str, Any]])
def get_random_cases(limit: int = 10):
    """
    Fetch random cases for exploration.
    """
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT case_id, text, summary, decision
            FROM cases
            ORDER BY RANDOM()
            LIMIT %s
        """, (limit,))
        
        rows = cursor.fetchall()
        
        # Convert RealDictRow or tuple to clean dict list
        # Assuming fetchall() returns list of dict-like objects if using RealDictCursor,
        # or we need to ensure DatabaseConnection is configured that way.
        # Based on previous code in 1_Case_Explorer.py:
        # row["case_id"], row["text"], etc. implies dictionary access.
        
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    except Exception as e:
        print(f"Error fetching random cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cases/{case_id}", response_model=Dict[str, Any])
def get_case_details(case_id: str):
    """
    Get full details for a specific case.
    """
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT case_id, text, summary, decision, decision_reason
            FROM cases
            WHERE case_id = %s
        """, (case_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
            
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

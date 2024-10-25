from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from rag_system import RAGSystem
import uvicorn

app = FastAPI(title="RAG System API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Set to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize RAG system
rag_system = RAGSystem()

class QueryRequest(BaseModel):
    query: str
    mode: str
    k: int = 3

@app.post("/api/query")
async def query(request: QueryRequest):
    try:
        response = rag_system.query(
            user_query=request.query,
            mode=request.mode,
            k=request.k
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
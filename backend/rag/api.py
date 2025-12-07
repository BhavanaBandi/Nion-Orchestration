from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

import logging
from .ingest import ingest_project_docs

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize vector store once at import time
try:
    vector_store = ingest_project_docs()
    logger.info(f"RAG Vector Store initialized with {len(vector_store.texts)} documents.")
except Exception as e:
    logger.error(f"Failed to initialize RAG Vector Store: {e}")
    vector_store = None

class ChatRequest(BaseModel):
    question: str
    top_k: int = 3

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not vector_store:
        raise HTTPException(status_code=500, detail="Vector store not initialized")
    results = vector_store.query(request.question, top_k=request.top_k)
    
    if not results:
        return ChatResponse(answer="I couldn't find any specific information about that in the project documentation.", sources=[])

    # Construct prompt for RAG
    context_text = "\n\n".join(results)
    system_prompt = (
        "You are a helpful Project Assistant for the Nion Orchestration Engine. "
        "Answer the user's question based strictly on the context provided below. "
        "If the answer isn't in the context, say you don't know."
    )
    user_prompt = f"Context:\n{context_text}\n\nQuestion: {request.question}"

    try:
        from llm.grok_client import llm_client
        answer = await llm_client.complete(system_prompt, user_prompt, temperature=0.3)
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        answer = "I found some relevant documents but failed to generate a summary. Here are the raw sources."
        # Fallback to just showing results if LLM fails
        if not answer:
             answer = "\n".join(results)

    return ChatResponse(answer=answer, sources=results)

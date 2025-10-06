from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging

from ..services import rerank_service

router = APIRouter(prefix="/api/v1/ai", tags=["AI ReRank"])
logger = logging.getLogger(__name__)


class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    provider: str = "huggingface"
    top_k: int = 5


@router.post("/rerank")
async def rerank_documents(request: RerankRequest):
    """
    Re-rank a list of documents using the specified model.
    """
    try:
        logger.info(f"Rerank request: model={request.model}, provider={request.provider}")
        ranked = rerank_service.rerank_documents(
            query=request.query,
            documents=request.documents,
            model_name=request.model,
            provider=request.provider,
        )
        return {"ranked_documents": ranked[:request.top_k]}

    except Exception as e:
        logger.error(f"Rerank failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

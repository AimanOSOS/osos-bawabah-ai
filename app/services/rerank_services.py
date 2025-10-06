import logging
from typing import List, Dict

from sentence_transformers import CrossEncoder, SentenceTransformer
import torch

logger = logging.getLogger(__name__)

# Cache models
_MODEL_CACHE: Dict[str, object] = {}


def get_model(model_name: str, mode: str):
    """Load and cache the reranking model."""
    global _MODEL_CACHE

    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]

    if mode == "cross":
        model = CrossEncoder(model_name)
    else:
        model = SentenceTransformer(model_name)

    _MODEL_CACHE[model_name] = model
    logger.info(f"Loaded reranker model: {model_name}")
    return model


def rerank_documents(query: str, documents: List[str], model_name: str, provider: str = "huggingface") -> List[Dict]:
    """Perform reranking using cross-encoder or bi-encoder."""
    if provider == "embedding":
        # Bi-encoder
        model = get_model(model_name, "bi")
        q_emb = model.encode(query, convert_to_tensor=True)
        d_embs = model.encode(documents, convert_to_tensor=True)
        scores = torch.nn.functional.cosine_similarity(q_emb, d_embs)
        ranked = [
            {"document": doc, "score": float(score)}
            for doc, score in zip(documents, scores)
        ]
        ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)
        return ranked

    else:
        # Cross-encoder
        model = get_model(model_name, "cross")
        pairs = [(query, doc) for doc in documents]
        scores = model.predict(pairs)
        ranked = [
            {"document": doc, "score": float(score)}
            for doc, score in zip(documents, scores)
        ]
        ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)
        return ranked

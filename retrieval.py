"""Embed the chunks from processed/chunks.jsonl into ChromaDB and expose a
retrieval function that returns the top-k most relevant chunks for a query.
"""
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = Path("processed/chunks.jsonl")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "unofficial_guide"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def load_chunks() -> list[dict]:
    return [json.loads(line) for line in CHUNKS_PATH.open()]


def sanitize_metadata(meta: dict) -> dict:
    """ChromaDB metadata values must be str, int, float, or bool."""
    clean = {}
    for k, v in meta.items():
        if isinstance(v, list):
            clean[k] = ", ".join(str(x) for x in v)
        elif v is None:
            continue
        else:
            clean[k] = v
    return clean


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )

    chunks = load_chunks()
    if collection.count() == len(chunks):
        return collection  # already embedded, nothing to do

    if collection.count() > 0:
        client.delete_collection(COLLECTION_NAME)
        collection = client.get_or_create_collection(
            COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    model = get_model()
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64).tolist()

    batch_size = 512
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        collection.add(
            ids=[c["chunk_id"] for c in batch],
            embeddings=embeddings[i:i + batch_size],
            documents=[c["text"] for c in batch],
            metadatas=[
                sanitize_metadata({
                    "doc_id": c["doc_id"],
                    "source": c["source"],
                    "type": c["type"],
                    "chunk_index": c["chunk_index"],
                    **c["metadata"],
                })
                for c in batch
            ],
        )
    return collection


def retrieve(query: str, k: int = 5) -> list[dict]:
    collection = get_collection()
    query_embedding = get_model().encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)

    hits = []
    for text, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": text, "source": meta.get("source"), "distance": distance, "metadata": meta})
    return hits


if __name__ == "__main__":
    test_queries = [
        "What time does the first weekday Clover at the Parks shuttle depart, and from which stop?",
        "What do tenants say about who manages Clover at the Parks and about the leasing manager there?",
        "According to Howard's off-campus housing FAQ, what should a student do if someone asks them to send money before seeing the apartment or meeting the landlord?",
    ]
    for q in test_queries:
        print(f"\n=== Query: {q} ===")
        for rank, hit in enumerate(retrieve(q, k=5), start=1):
            print(f"[{rank}] distance={hit['distance']:.3f} source={hit['source']}")
            print(f"    {hit['text']}")

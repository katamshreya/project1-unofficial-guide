"""Embedding and retrieval stage for the Unofficial Guide RAG system.

Takes the cleaned chunks produced by ingest.py, embeds them with the
all-MiniLM-L6-v2 sentence-transformers model, and stores them in a local
(persistent) ChromaDB collection. Embedding only happens once: re-running the
script reuses the existing collection. Exposes retrieve(query, k) for the
generation stage (generate.py).

Run directly to (re)build the index and run a few sample queries:

    python embed.py

Everything runs locally — no API keys required.
"""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import ingest

# Embedding model and storage locations (see planning.md, Retrieval Approach).
MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "professor_reviews"

# Embed in batches so we don't hold every vector in memory at once. The corpus
# is small, but this keeps the pattern correct if it grows.
EMBED_BATCH_SIZE = 64

# Module-level singletons so the model and client load only once per process,
# and so retrieve() can be imported and called without re-running setup.
_model: SentenceTransformer | None = None
_collection = None


def get_model() -> SentenceTransformer:
    """Load (once) and return the shared embedding model."""
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME} ...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_collection():
    """Return the persistent ChromaDB collection, creating it if needed.

    On first call this builds the index: it pulls chunks from ingest(), embeds
    them, and adds them to the collection. If the collection already holds
    documents, embedding is skipped so repeated runs are fast.
    """
    global _collection
    if _collection is not None:
        return _collection

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # Cosine distance matches how all-MiniLM-L6-v2 embeddings are compared.
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() > 0:
        print(f"Collection '{COLLECTION_NAME}' already has "
              f"{collection.count()} chunks — skipping embedding.")
        _collection = collection
        return _collection

    print("Empty collection — running ingestion and embedding ...")
    chunks = ingest()
    if not chunks:
        raise RuntimeError("ingest() returned no chunks; nothing to embed.")

    ids = [f"{c['source']}_chunk_{c['chunk_index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {"source": c["source"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]

    model = get_model()
    embeddings = model.encode(
        documents,
        batch_size=EMBED_BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
    ).tolist()

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"Embedded and stored {len(ids)} chunks in '{COLLECTION_NAME}'.")

    _collection = collection
    return _collection


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Return the top-k most similar chunks to `query`.

    Each result dict has keys: "text", "source", "chunk_index", "distance".
    Results are ordered closest-first (smaller cosine distance = more similar).
    """
    collection = get_collection()
    query_embedding = get_model().encode([query], convert_to_numpy=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
    )

    # Chroma returns each field as a list-of-lists (one inner list per query);
    # we issued a single query, so unwrap index 0.
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": dist,
        }
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]


if __name__ == "__main__":
    # Build the index (or reuse it) before querying.
    get_collection()

    test_queries = [
        "What do students say about Mike Scott's exams?",
        "Should I take Chatterjee or Joshi for CS429?",
        "Is CS439 harder than CS429?",
    ]

    for query in test_queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)
        for i, result in enumerate(retrieve(query, k=5), start=1):
            print(f"\n[{i}] distance={result['distance']:.4f} | "
                  f"{result['source']} | chunk {result['chunk_index']}")
            print(result["text"])

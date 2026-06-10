"""Document ingestion and chunking pipeline for the Unofficial Guide RAG system.

Loads the plain-text source documents (Rate My Professors reviews and Reddit
threads), cleans them, and splits them into overlapping character chunks that
carry their source filename and position. The output of `ingest()` is the input
to the embedding stage (embed.py).

Run directly to preview the result:

    python ingest.py
"""

import re
from pathlib import Path

# Folder containing the .txt source documents, relative to this file.
DOCUMENTS_DIR = Path(__file__).parent / "documents"

# Chunking parameters (see the Chunking Strategy section of planning.md).
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
MIN_CHUNK_LENGTH = 50

# Structural markers that carry no semantic content and should be dropped during
# cleaning: section dividers like "--- REVIEWS ---" and bare URL lines.
_DIVIDER_RE = re.compile(r"^-{2,}.*-{2,}$")
_URL_LINE_RE = re.compile(r"^URL:\s*\S+$", re.IGNORECASE)


def clean_text(raw: str) -> str:
    """Strip leftover formatting artifacts and normalize whitespace.

    Removes section-divider lines ("--- COMMENTS ---"), standalone URL lines,
    and blank lines, then collapses runs of whitespace so the document becomes a
    single continuous stream of readable text. Rating headers, tag lines, and the
    review/comment bodies are kept because they carry retrieval-relevant signal.
    """
    cleaned_lines = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if _DIVIDER_RE.match(line) or _URL_LINE_RE.match(line):
            continue
        # Collapse any internal runs of whitespace to a single space.
        cleaned_lines.append(re.sub(r"\s+", " ", line))
    return " ".join(cleaned_lines)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into fixed-size character chunks with a sliding-window overlap."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        # Stop once this chunk reached the end of the text.
        if start + chunk_size >= len(text):
            break
    return chunks


def load_documents(documents_dir: Path = DOCUMENTS_DIR) -> dict[str, str]:
    """Read every .txt file in the documents folder into {filename: raw_text}."""
    txt_files = sorted(documents_dir.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {documents_dir!s}")
    return {path.name: path.read_text(encoding="utf-8") for path in txt_files}


def ingest(documents_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    """Run the full pipeline and return chunk dicts.

    Each dict has keys: "text", "source" (filename), and "chunk_index"
    (0-based index of the chunk within its source document).
    """
    records = []
    for source, raw in load_documents(documents_dir).items():
        cleaned = clean_text(raw)
        chunk_index = 0
        for chunk in chunk_text(cleaned):
            if len(chunk) < MIN_CHUNK_LENGTH:
                continue
            records.append({
                "text": chunk,
                "source": source,
                "chunk_index": chunk_index,
            })
            chunk_index += 1
    return records


if __name__ == "__main__":
    chunks = ingest()

    print("=" * 70)
    print("Sample chunks")
    print("=" * 70)
    for chunk in chunks[:5]:
        print(f"\n[{chunk['source']} | chunk {chunk['chunk_index']} | "
              f"{len(chunk['text'])} chars]")
        print(chunk["text"])

    print("\n" + "=" * 70)
    print(f"Total chunks: {len(chunks)}")
    print("=" * 70)

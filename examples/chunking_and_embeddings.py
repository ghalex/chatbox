"""
Chunking & Embeddings Example
==============================
This example shows how to:
  1. Take a raw document
  2. Split it into chunks using 3 different strategies
  3. Generate an embedding vector for each chunk via Voyage AI

Voyage AI has a free tier (200M tokens free) — great for students!
  Sign up : https://dash.voyageai.com
  Docs    : https://docs.voyageai.com

Install dependencies:
    pip install voyageai python-dotenv

Add to your .env file:
    VOYAGE_API_KEY="pa-..."
"""

import re
import voyageai
from dotenv import load_dotenv
import os

load_dotenv()

client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])

# ---------------------------------------------------------------------------
# Sample document
# ---------------------------------------------------------------------------

DOCUMENT = """
## Introduction

Artificial intelligence (AI) is transforming how we interact with technology.
From voice assistants to recommendation engines, AI is embedded in daily life.
It learns from data, identifies patterns, and makes decisions with minimal human input.

## How Machine Learning Works

Machine learning is a subset of AI. Instead of being explicitly programmed,
models learn from examples. A model is trained on labelled data, adjusts its
internal parameters to minimise errors, and then generalises to new inputs.
Common algorithms include linear regression, decision trees, and neural networks.

## Neural Networks and Deep Learning

Neural networks are loosely inspired by the human brain. They consist of layers
of interconnected nodes (neurons). Deep learning refers to networks with many
layers. These deep networks excel at tasks like image recognition, natural
language processing, and speech synthesis.

## Embeddings

Embeddings are dense numerical representations of text (or other data).
They capture semantic meaning so that similar concepts end up close together
in vector space. This makes them ideal for search, clustering, and retrieval-
augmented generation (RAG) pipelines.
"""

# ---------------------------------------------------------------------------
# Chunking strategies
# ---------------------------------------------------------------------------

def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    """Split text into fixed-size character windows with optional overlap."""
    chunks = []
    start_idx = 0

    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))
        chunks.append(text[start_idx:end_idx])
        start_idx = end_idx - chunk_overlap if end_idx < len(text) else len(text)

    return chunks


def chunk_by_sentence(text, max_sentences_per_chunk=3, overlap_sentences=1):
    """Split text into groups of sentences with one-sentence overlap."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks = []
    start_idx = 0

    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        chunks.append(" ".join(sentences[start_idx:end_idx]))
        start_idx += max_sentences_per_chunk - overlap_sentences
        if start_idx < 0:
            start_idx = 0

    return chunks


def chunk_by_section(document_text):
    """Split a Markdown document on level-2 headings (## ...)."""
    return [s.strip() for s in re.split(r"\n## ", document_text) if s.strip()]


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------

def embed(texts: list[str], model: str = "voyage-4") -> list[list[float]]:
    """Return one embedding vector per text using the Voyage AI Embeddings API.

    Free-tier models:
      voyage-4       →  2048 dimensions (highest quality)
      voyage-3-lite  →  512 dimensions  (fastest, cheapest)
      voyage-3       →  1024 dimensions (higher quality)
    """
    result = client.embed(texts, model=model, output_dimension=2048)
    return result.embeddings


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

def log_chunks(chunks: list[str]) -> None:
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}:")
        print("-" * 60)
        print(chunk)
        print("-" * 60)
        print("\n")

def log_chunks_and_embeddings(chunks: list[str], embeddings: list[list[float]]) -> None:
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}:")
        print(f"Embedding: {embeddings[i][:5]}")
        print("-" * 60)
        print(chunk)
        print("-" * 60)
        print("\n")

def log_embeddings(embeddings: list[list[float]]) -> None:
    for i, embedding in enumerate(embeddings):
        print(f"Embedding {i + 1}:")
        print(embedding[:5])
        print("-" * 60)
        print("\n")

def main():
    print("Document length:", len(DOCUMENT), "characters")

    chunks = chunk_by_char(DOCUMENT, chunk_size=150, chunk_overlap=20)
    #chunks = chunk_by_section(DOCUMENT)
    embeddings = embed(chunks)


    log_embeddings(embeddings)

    # demo_strategy(
    #     "By character (size=150, overlap=20)",
    #     chunks,
    # )

    # demo_strategy(
    #     "By sentence (3 sentences, 1 overlap)",
    #     chunk_by_sentence(DOCUMENT, max_sentences_per_chunk=3, overlap_sentences=1),
    # )

    # demo_strategy(
    #     "By section (## headings)",
    #     chunk_by_section(DOCUMENT),
    # )


if __name__ == "__main__":
    main()

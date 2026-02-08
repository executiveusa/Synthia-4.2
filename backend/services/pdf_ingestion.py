"""
Synthia 4.2 - PDF Knowledge Ingestion Pipeline

Extracts text from PDFs, chunks it, and loads into the persistent memory
knowledge base. Synthia can then reference this knowledge during conversations.

Supports:
- PDF text extraction (PyMuPDF/fitz or pdfplumber fallback)
- Smart chunking (paragraph-aware, respects headings)
- Deduplication (content hash)
- Category tagging
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    
    # Try PyMuPDF (fitz) first - fastest
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        text = "\n\n".join(pages)
        logger.info("Extracted %d chars from %s (PyMuPDF)", len(text), pdf_path)
        return text
    except ImportError:
        pass

    # Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    pages.append(t)
        text = "\n\n".join(pages)
        logger.info("Extracted %d chars from %s (pdfplumber)", len(text), pdf_path)
        return text
    except ImportError:
        pass

    # Try PyPDF2
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
        text = "\n\n".join(pages)
        logger.info("Extracted %d chars from %s (PyPDF2)", len(text), pdf_path)
        return text
    except ImportError:
        pass

    raise RuntimeError(
        "No PDF library available. Install one: pip install PyMuPDF pdfplumber PyPDF2"
    )


def chunk_text(
    text: str,
    max_chunk_size: int = 1500,
    overlap: int = 200,
) -> list[str]:
    """
    Split text into overlapping chunks for knowledge storage.
    Respects paragraph boundaries where possible.
    """
    if not text.strip():
        return []

    # Split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # If adding this paragraph would exceed limit, save current and start new
        if current_chunk and len(current_chunk) + len(para) + 2 > max_chunk_size:
            chunks.append(current_chunk.strip())
            # Keep overlap from end of previous chunk
            if overlap > 0:
                current_chunk = current_chunk[-overlap:] + "\n\n" + para
            else:
                current_chunk = para
        else:
            current_chunk = (current_chunk + "\n\n" + para).strip()
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Handle case where single paragraphs are very long
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size * 2:
            # Force split long chunks
            for i in range(0, len(chunk), max_chunk_size):
                sub = chunk[i:i + max_chunk_size + overlap]
                if sub.strip():
                    final_chunks.append(sub.strip())
        else:
            final_chunks.append(chunk)
    
    return final_chunks


def ingest_pdf(
    pdf_path: str,
    category: str = "training",
    memory_store=None,
) -> dict:
    """
    Full pipeline: Extract text from PDF → chunk → store in memory.
    
    Returns:
        {"source": filename, "chunks": N, "new_chunks": N, "total_chars": N}
    """
    if memory_store is None:
        from services.memory import get_memory_store
        memory_store = get_memory_store()

    filename = os.path.basename(pdf_path)
    logger.info("Ingesting PDF: %s (category: %s)", filename, category)

    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        return {"source": filename, "chunks": 0, "new_chunks": 0, "total_chars": 0}

    # Chunk
    chunks = chunk_text(text)
    
    # Store chunks
    new_count = 0
    for i, chunk in enumerate(chunks):
        is_new = memory_store.add_knowledge(
            source=filename,
            content=chunk,
            category=category,
            chunk_index=i,
        )
        if is_new:
            new_count += 1

    result = {
        "source": filename,
        "chunks": len(chunks),
        "new_chunks": new_count,
        "total_chars": len(text),
    }
    logger.info("PDF ingestion complete: %s", result)
    return result


def ingest_text_file(
    file_path: str,
    category: str = "training",
    memory_store=None,
) -> dict:
    """Ingest a plain text, markdown, or JSONL file into knowledge base."""
    if memory_store is None:
        from services.memory import get_memory_store
        memory_store = get_memory_store()

    filename = os.path.basename(file_path)
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    if file_path.endswith(".jsonl"):
        # Extract content from JSONL training data
        import json
        lines = text.strip().split("\n")
        combined = []
        for line in lines:
            try:
                obj = json.loads(line)
                messages = obj.get("messages", [])
                for msg in messages:
                    if msg.get("role") in ("assistant", "system"):
                        combined.append(msg["content"])
            except json.JSONDecodeError:
                continue
        text = "\n\n".join(combined)

    chunks = chunk_text(text)
    new_count = 0
    for i, chunk in enumerate(chunks):
        is_new = memory_store.add_knowledge(
            source=filename, content=chunk, category=category, chunk_index=i
        )
        if is_new:
            new_count += 1

    return {
        "source": filename,
        "chunks": len(chunks),
        "new_chunks": new_count,
        "total_chars": len(text),
    }


def ingest_directory(
    dir_path: str,
    category: str = "training",
    extensions: tuple = (".pdf", ".txt", ".md", ".jsonl"),
) -> list[dict]:
    """Ingest all supported files from a directory."""
    results = []
    for root, _, files in os.walk(dir_path):
        for filename in sorted(files):
            if any(filename.lower().endswith(ext) for ext in extensions):
                filepath = os.path.join(root, filename)
                try:
                    if filename.lower().endswith(".pdf"):
                        result = ingest_pdf(filepath, category)
                    else:
                        result = ingest_text_file(filepath, category)
                    results.append(result)
                except Exception as e:
                    logger.error("Failed to ingest %s: %s", filepath, e)
                    results.append({"source": filename, "error": str(e)})
    return results


__all__ = [
    "extract_text_from_pdf",
    "chunk_text", 
    "ingest_pdf",
    "ingest_text_file",
    "ingest_directory",
]

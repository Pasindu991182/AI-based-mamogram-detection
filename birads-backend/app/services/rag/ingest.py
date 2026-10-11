"""Build the FAISS knowledge-base index (RAG stages 1-4).

Run once (or whenever sources change):

    python -m scripts.build_rag_index

Downloads the guideline PDFs/web pages, splits them into chunks, embeds them
with OpenAI, and persists a FAISS index to settings.RAG_INDEX_DIR. LangChain
and network access are only needed at build time, not at request time.
"""
from __future__ import annotations

import glob
import os
import tempfile
import urllib.parse
import urllib.request

from app.core.config import settings
from app.core.logging import get_logger
from app.services.rag.knowledge_sources import PDF_URLS, WEB_URLS

logger = get_logger(__name__)


def _download_pdf(url: str) -> str:
    """Download a PDF to a temp file (robust across LangChain versions)."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    fd, path = tempfile.mkstemp(suffix=".pdf")
    with urllib.request.urlopen(req, timeout=120) as resp, os.fdopen(fd, "wb") as f:
        f.write(resp.read())
    return path


def _load_documents() -> list:
    """RAG stage 1 — Load. Returns a list of LangChain Document objects."""
    from langchain_community.document_loaders import (
        PyPDFLoader,
        TextLoader,
        WebBaseLoader,
    )

    docs: list = []

    # 1a. Guideline PDFs by URL
    for url in PDF_URLS:
        try:
            local = _download_pdf(url)
            loaded = PyPDFLoader(local).load()
            name = urllib.parse.unquote(url.split("/")[-1])
            for d in loaded:
                d.metadata["source"] = name
            docs.extend(loaded)
            logger.info("PDF loaded: %s (%d pages)", name, len(loaded))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipped PDF %s — %s", url, exc)

    # 1b. Guideline web pages
    for url in WEB_URLS:
        try:
            loaded = WebBaseLoader(url).load()
            for d in loaded:
                d.metadata["source"] = url
            docs.extend(loaded)
            logger.info("Web loaded: %s", url)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipped web %s — %s", url, exc)

    # 1c. Local documents (drop PDFs / .txt into rag_docs/ — e.g. generated reports)
    local_dir = str(settings.RAG_DOCS_DIR)
    for path in glob.glob(os.path.join(local_dir, "*")):
        try:
            loader = (
                PyPDFLoader(path)
                if path.lower().endswith(".pdf")
                else TextLoader(path, encoding="utf-8")
            )
            loaded = loader.load()
            for d in loaded:
                d.metadata["source"] = os.path.basename(path)
            docs.extend(loaded)
            logger.info("Local loaded: %s", os.path.basename(path))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipped local %s — %s", path, exc)

    return docs


def build_index() -> dict:
    """Full ingest pipeline. Returns a small summary dict."""
    if not settings.rag_key_configured:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to birads-backend/.env before building."
        )

    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    logger.info("Loading documents…")
    docs = _load_documents()
    if not docs:
        raise RuntimeError("No documents could be loaded — check your network/sources.")

    # Stage 2 — Split
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP,
        add_start_index=True,
    )
    chunks = splitter.split_documents(docs)
    logger.info("Split into %d chunks.", len(chunks))

    # Stages 3-4 — Embed + store
    embeddings = OpenAIEmbeddings(
        model=settings.RAG_EMBED_MODEL, api_key=settings.OPENAI_API_KEY
    )
    logger.info("Embedding %d chunks with %s…", len(chunks), settings.RAG_EMBED_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    settings.RAG_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(settings.RAG_INDEX_DIR))
    logger.info("Saved FAISS index to %s", settings.RAG_INDEX_DIR)

    return {
        "documents": len(docs),
        "chunks": len(chunks),
        "index_dir": str(settings.RAG_INDEX_DIR),
    }

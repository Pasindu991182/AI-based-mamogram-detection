"""Build the Tier 6 RAG knowledge-base index.

Usage (from birads-backend/, with the venv active and OPENAI_API_KEY set):

    python -m scripts.build_rag_index

Downloads the guideline PDFs/web pages, embeds them, and saves a FAISS index
to rag_index/. Re-run whenever you change knowledge_sources.py or add files
to rag_docs/.
"""
from app.services.rag.ingest import build_index


def main() -> None:
    print("Building RAG knowledge-base index… (this downloads PDFs + calls OpenAI)")
    summary = build_index()
    print("\n✅ Done.")
    print(f"   Documents: {summary['documents']}")
    print(f"   Chunks:    {summary['chunks']}")
    print(f"   Index dir: {summary['index_dir']}")


if __name__ == "__main__":
    main()

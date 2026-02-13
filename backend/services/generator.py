"""
LLM answer generator — uses Google Gemini API to generate cited answers.
"""
import os
from google import genai

from backend.config import GEMINI_API_KEY

# ── Singleton client ──
_client = None

PROMPT_TEMPLATE = """You are an internal knowledge base assistant.
Answer the question ONLY using the context provided below.
If the context does not contain enough information to answer, say "I don't have enough information to answer this question based on the available documents."

Include citations like [1], [2] referring to the numbered sources below.
Be concise but thorough. Use bullet points where appropriate.

Question: {question}

Sources:
{context}

Answer:"""


def get_gemini_client():
    global _client
    if _client is None:
        api_key = GEMINI_API_KEY
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Get a free key at https://aistudio.google.com/apikey "
                "and add it to your .env file."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def generate_answer(question: str, ranked_chunks: list[dict]) -> dict:
    """
    Generate an AI answer using Gemini, grounded in the ranked chunks.

    Args:
        question: The user's question.
        ranked_chunks: Top chunks from search+rerank.

    Returns:
        Dict with 'answer' text and 'citations' list.
    """
    if not ranked_chunks:
        return {
            "answer": "I couldn't find any relevant documents to answer your question.",
            "citations": [],
        }

    # Build numbered context
    context_lines = []
    for i, chunk in enumerate(ranked_chunks, start=1):
        title = chunk.get("doc_title", "Unknown")
        dept = chunk.get("department", "")
        text = chunk["text"][:600]  # truncate long chunks
        context_lines.append(f"[{i}] ({title} — {dept} dept): {text}")

    prompt = PROMPT_TEMPLATE.format(
        question=question,
        context="\n\n".join(context_lines),
    )

    # Call Gemini
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        answer_text = response.text
    except Exception as e:
        error_msg = str(e)
        print(f"  ⚠ Gemini API error: {error_msg}")
        # Return the search results even if LLM fails
        answer_text = (
            f"[LLM unavailable — showing search results only]\n\n"
            f"I found {len(ranked_chunks)} relevant passages but couldn't generate "
            f"an AI summary. Error: {error_msg[:200]}\n\n"
            f"Top result from '{ranked_chunks[0].get('doc_title', 'Unknown')}':\n"
            f"{ranked_chunks[0]['text'][:500]}"
        )

    # Parse citations from the answer
    citations = parse_citations(answer_text, ranked_chunks)

    return {
        "answer": answer_text,
        "citations": citations,
    }


def parse_citations(answer: str, chunks: list[dict]) -> list[dict]:
    """
    Extract [N] citation markers from the answer and map to source chunks.
    """
    import re
    markers = set(int(m) for m in re.findall(r"\[(\d+)\]", answer))

    citations = []
    for marker in sorted(markers):
        idx = marker - 1  # convert 1-indexed to 0-indexed
        if 0 <= idx < len(chunks):
            chunk = chunks[idx]
            citations.append({
                "marker": marker,
                "doc_title": chunk.get("doc_title", "Unknown"),
                "doc_id": chunk.get("doc_id", ""),
                "department": chunk.get("department", ""),
                "chunk_text": chunk["text"][:300],  # preview
            })

    return citations

"""
Text chunker — splits parsed text into overlapping chunks.
"""
import re


def chunk_text(text: str, max_tokens: int = 400, overlap_tokens: int = 80) -> list[str]:
    """
    Split text into chunks of roughly max_tokens words with overlap.

    Strategy:
    1. Split by double-newlines (paragraphs).
    2. Merge small paragraphs until reaching ~max_tokens words.
    3. Add overlap from the end of the previous chunk.

    Returns:
        List of chunk strings.
    """
    # Split into paragraphs
    paragraphs = re.split(r"\n\s*\n", text.strip())
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if not paragraphs:
        return []

    chunks = []
    current_chunk_words = []

    for para in paragraphs:
        para_words = para.split()

        # If adding this paragraph exceeds max_tokens and we already have content
        if current_chunk_words and (len(current_chunk_words) + len(para_words)) > max_tokens:
            # Save current chunk
            chunks.append(" ".join(current_chunk_words))
            # Start new chunk with overlap from end of previous
            overlap_words = current_chunk_words[-overlap_tokens:] if len(current_chunk_words) > overlap_tokens else current_chunk_words[:]
            current_chunk_words = overlap_words + para_words
        else:
            current_chunk_words.extend(para_words)

    # Don't forget the last chunk
    if current_chunk_words:
        chunks.append(" ".join(current_chunk_words))

    return chunks


def chunk_document_segments(segments: list[dict], max_tokens: int = 400, overlap_tokens: int = 80) -> list[str]:
    """
    Chunk all segments from a parsed document into a flat list of chunks.

    Args:
        segments: List of {"text": "...", "page": N} from the parser.

    Returns:
        List of chunk strings.
    """
    # Combine all segments into one text block
    full_text = "\n\n".join(seg["text"] for seg in segments)
    return chunk_text(full_text, max_tokens=max_tokens, overlap_tokens=overlap_tokens)

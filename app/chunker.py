import re


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]

    chunks: list[str] = []
    current_words: list[str] = []

    for para in paragraphs:
        para_words = para.split()


        if len(para_words) > chunk_size:
            for i in range(0, len(para_words), chunk_size - overlap):
                sub_words = para_words[i : i + chunk_size]
                if sub_words:
                    chunks.append(" ".join(sub_words))
            continue

        current_words.extend(para_words)

        if len(current_words) >= chunk_size:
            chunks.append(" ".join(current_words))

            current_words = current_words[-overlap:] if overlap else []


    if current_words:
        chunks.append(" ".join(current_words))

    return [c for c in chunks if c.strip()]

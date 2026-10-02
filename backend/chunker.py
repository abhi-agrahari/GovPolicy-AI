def chunk_pages(pages, chunk_size=800, overlap=100):
    chunks = []

    for page in pages:
        text = page["text"].strip()
        page_number = page["page"]

        if not text:
            continue

        start = 0
        chunk_number = 1

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # splitting at a word boundary
            if end < len(text):
                split_at = text.rfind(" ", start, end)
                if split_at > start:
                    end = split_at

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "page": page_number,
                    "chunk": chunk_number,
                    "text": chunk_text
                })
                chunk_number += 1

            if end >= len(text):
                break

            start = max(end - overlap, start + 1)

    return chunks
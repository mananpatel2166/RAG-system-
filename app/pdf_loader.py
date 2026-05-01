from pathlib import Path
import fitz  


def extract_text_from_pdf(path: str | Path) -> str:
    
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages: list[str] = []
    with fitz.open(str(path)) as doc:
        for page_num, page in enumerate(doc, start=1):
            try:
                text = page.get_text("text")
                if text.strip():
                    pages.append(f"[Page {page_num}]\n{text.strip()}")
            except Exception as exc:
               
                print(f"Warning: could not read page {page_num}: {exc}")

    return "\n\n".join(pages)

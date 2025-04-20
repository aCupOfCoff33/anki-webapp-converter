from io import BytesIO, StringIO, TextIOWrapper
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from docx import Document
import csv, re

app = FastAPI(title="Anki Flashcard Converter")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],  # frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Regex for parsing DOCX
FRONT_RE = re.compile(r"^Front:\s*(.*)", flags=re.I)
BACK_RE = re.compile(r"^Back:\s*(.*)", flags=re.I)
CLOZE_RE = re.compile(r"{{c\d+::")


def extract_cards(doc_path: Path):
    """Yield (front, back) pairs from a .docx file, even if they're tightly packed."""
    paragraphs = [
        p.text.strip() for p in Document(doc_path).paragraphs if p.text.strip()
    ]

    front = None
    for line in paragraphs:
        if line.lower().startswith("front:"):
            front = line.partition(":")[2].strip()
        elif line.lower().startswith("back:") and front:
            back = line.partition(":")[2].strip()
            yield front, back
            front = None


@app.post("/convert")
async def convert(files: List[UploadFile] = File(...)):
    """Accept DOCX files and return a TSV as download."""

    first_file_name = Path(files[0].filename).stem if files else "flashcards"

    text_buffer = StringIO()
    writer = csv.writer(text_buffer, delimiter="\t", lineterminator="\n")

    for uf in files:
        contents = await uf.read()
        tmp_path = Path("/tmp") / uf.filename
        tmp_path.write_bytes(contents)

        for front, back in extract_cards(tmp_path):
            if CLOZE_RE.search(front):
                writer.writerow([front, ""])
            else:
                writer.writerow([front, back])
        tmp_path.unlink(missing_ok=True)

    # Convert string to bytes for StreamingResponse
    byte_buffer = BytesIO(text_buffer.getvalue().encode("utf-8"))
    text_buffer.close()

    headers = {"Content-Disposition": f"attachment; filename={first_file_name}.tsv"}

    return StreamingResponse(
        byte_buffer, media_type="text/tab-separated-values", headers=headers
    )


@app.get("/ping")
async def ping():
    return {"ok": True}

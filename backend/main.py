from io import BytesIO
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import csv, re
from docx import Document

app = FastAPI(title="Anki Flashcard Converter")

# Allow local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONT_RE = re.compile(r"^Front:\s*(.*)", flags=re.I)
BACK_RE  = re.compile(r"^Back:\s*(.*)",  flags=re.I)
CLOZE_RE = re.compile(r"{{c\d+::")

def extract_cards(doc_path: Path):
    """Yield (front, back) tuples from a .docx file formatted with Front:/Back:"""
    front, back, collecting_back = None, [], False
    for para in Document(doc_path).paragraphs:
        txt = para.text.strip()
        m = FRONT_RE.match(txt)
        if m:
            if front is not None:
                yield front, "\n".join(back).strip()
            front, back, collecting_back = m.group(1), [], False
            continue
        m = BACK_RE.match(txt)
        if m:
            collecting_back = True
            inline = m.group(1)
            if inline:
                back.append(inline)
            continue
        if collecting_back and front is not None:
            back.append(txt)
    if front is not None:
        yield front, "\n".join(back).strip()

@app.post("/convert")
async def convert(files: List[UploadFile] = File(...)):
    """Accept DOCX files and return a TSV as download."""
    buffer = BytesIO()
    writer = csv.writer(buffer, delimiter="\t", lineterminator="\n")

    for uf in files:
        # Save to temp file in memory for python-docx
        contents = await uf.read()
        tmp_path = Path("/tmp") / uf.filename
        tmp_path.write_bytes(contents)
        for front, back in extract_cards(tmp_path):
            if CLOZE_RE.search(front):
                writer.writerow([front, ""])
            else:
                writer.writerow([front, back])
        tmp_path.unlink(missing_ok=True)

    buffer.seek(0)
    headers = {
        "Content-Disposition": "attachment; filename=flashcards.tsv"
    }
    return StreamingResponse(buffer, media_type="text/tab-separated-values", headers=headers)

@app.get("/ping")
async def ping():
    return {"ok": True}
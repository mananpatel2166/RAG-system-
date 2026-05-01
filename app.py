import os
import uuid
from pathlib import Path

from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename

from app.pdf_loader import extract_text_from_pdf
from app.chunker import chunk_text
from app.embedder import Embedder
from app.retriever import Retriever
from app.generator import Generator
from app.db import init_db, log_qa         


UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY" , "dev-secret-key")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024   

embedder  = Embedder()
generator = Generator()


retrievers: dict[str, Retriever] = {}

db_enabled = init_db()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_session_id() -> str:
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    return session["sid"]


@app.route("/")
def index():
    return {"message":"welcome"}


@app.route("/upload", methods=["POST"])
def upload():
   
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are accepted"}), 400

    filename  = secure_filename(file.filename)
    save_path = UPLOAD_FOLDER / filename
    file.save(save_path)


    raw_text = extract_text_from_pdf(save_path)
    if not raw_text.strip():
        return jsonify({"error": "Could not extract text from this PDF (may be scanned/image-only)"}), 422

    chunks    = chunk_text(raw_text, chunk_size=500, overlap=50)
    retriever = Retriever.from_chunks(chunks, embedder)

    sid = get_session_id()
    retrievers[sid] = retriever

    return jsonify({
        "message": "PDF processed successfully",
        "filename": filename,
        "chunks":   len(chunks),
    })


@app.route("/ask", methods=["POST"])
def ask():
    
    data     = request.get_json(force=True)
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Question is empty"}), 400

    sid = get_session_id()
    if sid not in retrievers:
        return jsonify({"error": "No document loaded. Please upload a PDF first."}), 400

    retriever = retrievers[sid]
    top_chunks = retriever.retrieve(question, embedder, k=4)
    context    = "\n\n".join(top_chunks)

    answer = generator.generate(question=question, context=context)

    if db_enabled:
        log_qa(session_id=sid, question=question, context=context, answer=answer)

    return jsonify({"answer": answer})


@app.route("/reset", methods=["POST"])
def reset():
    """Clear the current session's document index."""
    sid = get_session_id()
    retrievers.pop(sid, None)
    return jsonify({"message": "Session cleared"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

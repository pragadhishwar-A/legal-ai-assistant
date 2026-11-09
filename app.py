# app.py
# A minimal web app: upload a PDF, then ask questions about it.

import os
import logging

from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

import config
from ingest import ingest_document
from ask import ask_question

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_MB * 1024 * 1024
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    # Serves the frontend HTML page.
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file was sent."}), 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return jsonify({"error": "No file was selected."}), 400

    # Never trust the client's filename: strip path components and odd characters.
    filename = secure_filename(uploaded_file.filename)
    if not filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    # Check the real file signature, not just the extension.
    header = uploaded_file.stream.read(5)
    uploaded_file.stream.seek(0)
    if header != b"%PDF-":
        return jsonify({"error": "This file is not a valid PDF."}), 400

    save_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(save_path)

    try:
        ingest_document(save_path)
    except Exception as e:
        logger.error(f"Ingestion failed for {filename}: {e}")
        return jsonify({"error": "Could not process this PDF. It may be corrupted or password-protected."}), 500

    logger.info(f"Successfully ingested '{filename}'")
    return jsonify({"message": f"'{filename}' uploaded and processed."})


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    return jsonify({"error": f"File is too large. Maximum size is {config.MAX_UPLOAD_MB}MB."}), 413


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "No question was provided."}), 400

    logger.info("Question received (%d chars)", len(question))

    try:
        result = ask_question(question)
    except Exception as e:
        logger.error(f"Failed to answer question: {e}")
        return jsonify({"error": "Something went wrong generating an answer. Please try again."}), 500

    return jsonify(result)  # includes answer, sources, and confidence


if __name__ == "__main__":
    # Debug mode is opt-in. Never enable it in Docker or any public deployment.
    # Locally: $env:FLASK_DEBUG="1"; python app.py
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
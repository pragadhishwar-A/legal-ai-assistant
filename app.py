# app.py
# A minimal web app: upload a PDF, then ask questions about it.

import os
from flask import Flask, request, jsonify, render_template
from ingest import ingest_document
from ask import ask_question
from werkzeug.exceptions import RequestEntityTooLarge
import config
import logging

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
    # Serves the frontend HTML page (we'll create this in Step 10).
    return render_template("index.html")



@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file was sent."}), 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return jsonify({"error": "No file was selected."}), 400

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
    uploaded_file.save(save_path)

    try:
        ingest_document(save_path)
    except Exception as e:
        logger.error(f"Ingestion failed for {uploaded_file.filename}: {e}")
        return jsonify({"error": "Could not process this PDF. It may be corrupted or password-protected."}), 500

    return jsonify({"message": f"'{uploaded_file.filename}' uploaded and processed."})
    logger.info(f"Successfully ingested '{uploaded_file.filename}'")


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    return jsonify({"error": f"File is too large. Maximum size is {config.MAX_UPLOAD_MB}MB."}), 413


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question was provided."}), 400

    logger.info(f"Question received: {question}")

    try:
        result = ask_question(question)
    except Exception as e:
        logger.error(f"Failed to answer question: {e}")
        return jsonify({"error": "Something went wrong generating an answer. Please try again."}), 500

    return jsonify(result)  # now includes answer, sources, and confidence

if __name__ == "__main__":
    app.run(debug=True)
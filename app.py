# app.py
# A minimal web app: upload a PDF, then ask questions about it.

import os
from flask import Flask, request, jsonify, render_template
from ingest import ingest_document
from ask import ask_question

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    # Serves the frontend HTML page (we'll create this in Step 10).
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    # This runs when the browser sends a file to /upload.
    if "file" not in request.files:
        return jsonify({"error": "No file was sent."}), 400

    uploaded_file = request.files["file"]
    save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
    uploaded_file.save(save_path)

    # Run our ingestion logic on the newly-uploaded file.
    ingest_document(save_path)

    return jsonify({"message": f"'{uploaded_file.filename}' uploaded and processed."})


@app.route("/chat", methods=["POST"])
def chat():
    # This runs when the browser sends a question to /chat.
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question was provided."}), 400

    answer = ask_question(question)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
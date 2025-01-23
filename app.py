from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from werkzeug.utils import secure_filename
from chains import Chain
from utils import clean_text
from langchain_community.document_loaders import WebBaseLoader
app = Flask(__name__)

CORS(app)
# Configure upload folder and allowed extensions
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    jdLink = request.headers.get('jdLink')
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "Invalid Input"}), 400

    if file and allowed_file(file.filename):
        secure_name = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], secure_name)
        # filename = file.filename
        # filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        try:
            # Process the file (replace with your logic)
            # Example: Print the file size
            # file_size = os.path.getsize(filepath)
            # print(f"File size: {file_size} bytes")
            jd = ""
            print("Writing Mail")
            if jdLink != "":
                print("Jdlink is not null")
                loader = WebBaseLoader(jdLink)
                docs = loader.load()
                jd = clean_text(docs[0].page_content)
            llm = Chain()
            res = llm.write_mail(filepath,jd)

        finally:
            # Delete the file after processing
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"File {secure_name} deleted successfully.")
        
        return jsonify({"message": f"Success","Response":res}), 200
    else:
        return jsonify({"error": "Invalid file type. Only PDF files are allowed"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

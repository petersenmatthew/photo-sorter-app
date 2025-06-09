from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from face_sorter import register_faces, sort_photos  # import your functions
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure CORS to allow requests from your frontend
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "success", "message": "Backend is running!"})

@app.route("/register_faces", methods=["POST"])
def register():
    logger.debug("Received register_faces request")
    try:
        register_faces("uploads/ref", "encodings.pkl")
        return jsonify({"status": "success", "message": "Faces registered."})
    except Exception as e:
        logger.error(f"Error in register_faces: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload():
    logger.debug("Received upload request")
    try:
        ref_files = request.files.getlist("reference_faces")
        group_files = request.files.getlist("group_photos")
        
        logger.debug(f"Received {len(ref_files)} reference files and {len(group_files)} group files")

        os.makedirs("uploads/ref", exist_ok=True)
        os.makedirs("uploads/group", exist_ok=True)

        for f in ref_files:
            logger.debug(f"Saving reference file: {f.filename}")
            f.save(os.path.join("uploads/ref", f.filename))
        for f in group_files:
            logger.debug(f"Saving group file: {f.filename}")
            f.save(os.path.join("uploads/group", f.filename))

        result = sort_photos("uploads/ref", "uploads/group", "output", "encodings.pkl")
        logger.debug("Successfully processed photos")
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        logger.error(f"Error in upload: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from face_sorter import register_faces, sort_photos
import logging
import traceback
import shutil

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure CORS to allow requests from your frontend
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

def ensure_directories():
    """Ensure all required directories exist and are empty"""
    directories = ["uploads/ref", "uploads/group", "output"]
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "success", "message": "Backend is running!"})

@app.route("/register_faces", methods=["POST"])
def register():
    logger.debug("Received register_faces request")
    try:
        ensure_directories()
        ref_files = request.files.getlist("reference_faces")
        
        if not ref_files:
            logger.warning("No reference files received")
            return jsonify({
                "status": "success",
                "message": "No reference faces provided, skipping registration"
            })

        logger.debug(f"Received {len(ref_files)} reference files")
        
        for f in ref_files:
            logger.debug(f"Saving reference file: {f.filename}")
            f.save(os.path.join("uploads/ref", f.filename))

        encodings, names = register_faces("uploads/ref", "encodings.pkl")
        return jsonify({
            "status": "success", 
            "message": "Faces registered.",
            "details": {
                "faces_registered": len(encodings),
                "names": names
            }
        })
    except Exception as e:
        logger.error(f"Error in register_faces: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route("/upload", methods=["POST"])
def upload():
    logger.debug("Received upload request")
    try:
        ref_files = request.files.getlist("reference_faces")
        group_files = request.files.getlist("group_photos")
        
        logger.debug(f"Received {len(ref_files)} reference files and {len(group_files)} group files")

        # Save reference files if provided
        if ref_files:
            for f in ref_files:
                logger.debug(f"Saving reference file: {f.filename}")
                f.save(os.path.join("uploads/ref", f.filename))
            # Register faces if reference files were provided
            register_faces("uploads/ref", "encodings.pkl")

        # Save group files
        for f in group_files:
            logger.debug(f"Saving group file: {f.filename}")
            f.save(os.path.join("uploads/group", f.filename))

        # Sort photos
        result = sort_photos("uploads/ref", "uploads/group", "output", "encodings.pkl")
        logger.debug(f"Sort result: {result}")

        # Verify output directory contents
        output_files = []
        for root, dirs, files in os.walk("output"):
            for file in files:
                output_files.append(os.path.join(root, file))
        logger.debug(f"Files in output directory: {output_files}")

        return jsonify({
            "status": "success", 
            "result": result,
            "details": {
                "reference_files": [f.filename for f in ref_files],
                "group_files": [f.filename for f in group_files],
                "output_files": output_files
            }
        })
    except Exception as e:
        logger.error(f"Error in upload: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    ensure_directories()
    app.run(debug=True, host='0.0.0.0', port=5000)

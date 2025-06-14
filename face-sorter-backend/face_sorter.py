import face_recognition
import os
import pickle
from PIL import Image
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def register_faces(reference_dir="reference_faces", encodings_file="encodings.pkl"):
    encodings = []
    names = []

    logger.debug(f"Starting face registration from directory: {reference_dir}")
    for filename in os.listdir(reference_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(reference_dir, filename)
            logger.debug(f"Processing reference face: {filename}")

            try:
                image = face_recognition.load_image_file(image_path)
                face_encs = face_recognition.face_encodings(image)

                if face_encs:
                    encodings.append(face_encs[0])
                    names.append(os.path.splitext(filename)[0])
                    logger.debug(f"Successfully encoded face from {filename}")
                else:
                    logger.warning(f"No face found in reference image: {filename}")
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")

    with open(encodings_file, "wb") as f:
        pickle.dump((encodings, names), f)

    logger.info(f"Registered {len(encodings)} faces")
    return encodings, names

def sort_photos(reference_dir, group_dir, output_dir="output", encodings_file="encodings.pkl"):
    logger.debug(f"Starting photo sorting process")
    logger.debug(f"Reference directory: {reference_dir}")
    logger.debug(f"Group directory: {group_dir}")
    logger.debug(f"Output directory: {output_dir}")

    # Ensure output directory exists and is empty
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Check if we have reference faces
    if not os.path.exists(encodings_file) or os.path.getsize(encodings_file) == 0:
        logger.warning("No reference faces found. Creating a single output directory for all photos.")
        processed_count = 0

        # Simply copy all photos to the output directory
        for filename in os.listdir(group_dir):
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            try:
                image_path = os.path.join(group_dir, filename)
                output_path = os.path.join(output_dir, filename)
                Image.open(image_path).save(output_path)
                logger.info(f"Copied {filename} to output directory")
                processed_count += 1
            except Exception as e:
                logger.error(f"Error copying {filename}: {str(e)}")

        return {
            "status": "success",
            "message": "Photos copied to output directory (no face sorting performed)",
            "processed": processed_count,
            "matched": 0
        }

    try:
        # Load known encodings
        with open(encodings_file, "rb") as f:
            known_encodings, known_names = pickle.load(f)
        logger.debug(f"Loaded {len(known_encodings)} known face encodings")
    except Exception as e:
        logger.error(f"Error loading encodings file: {str(e)}")
        return {"status": "error", "message": "Failed to load face encodings"}

    processed_count = 0
    matched_count = 0
    unmatched_count = 0

    # Process each uploaded photo
    for filename in os.listdir(group_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        logger.debug(f"Processing group photo: {filename}")
        image_path = os.path.join(group_dir, filename)
        
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            logger.debug(f"Found {len(encodings)} faces in {filename}")

            if not encodings:
                logger.warning(f"No faces detected in {filename}")
                # Copy to unmatched directory
                unmatched_dir = os.path.join(output_dir, "unmatched")
                os.makedirs(unmatched_dir, exist_ok=True)
                Image.open(image_path).save(os.path.join(unmatched_dir, filename))
                unmatched_count += 1
                continue

            face_matched = False
            for face_encoding in encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
                logger.debug(f"Face matches found: {sum(matches)}")

                for i, is_match in enumerate(matches):
                    if is_match:
                        name = known_names[i]
                        person_dir = os.path.join(output_dir, name)
                        os.makedirs(person_dir, exist_ok=True)
                        image_output_path = os.path.join(person_dir, filename)

                        # Save copy of the image
                        Image.open(image_path).save(image_output_path)
                        logger.info(f"Saved {filename} to {person_dir}")
                        matched_count += 1
                        face_matched = True

            if not face_matched:
                # Copy to unmatched directory if no faces matched
                unmatched_dir = os.path.join(output_dir, "unmatched")
                os.makedirs(unmatched_dir, exist_ok=True)
                Image.open(image_path).save(os.path.join(unmatched_dir, filename))
                unmatched_count += 1

            processed_count += 1
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")

    logger.info(f"Processing complete. Processed {processed_count} photos, matched {matched_count} faces, {unmatched_count} unmatched")
    return {
        "status": "success",
        "message": "Sorting complete",
        "processed": processed_count,
        "matched": matched_count,
        "unmatched": unmatched_count
    }

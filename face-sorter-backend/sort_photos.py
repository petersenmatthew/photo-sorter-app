import face_recognition
import os
import pickle
from PIL import Image

ENCODINGS_FILE = "encodings.pkl"
uploads_dir = "uploads/"
output_dir = "output/"

# Load known encodings
with open(ENCODINGS_FILE, "rb") as f:
    known_encodings, known_names = pickle.load(f)

# Process each uploaded photo
for filename in os.listdir(uploads_dir):
    if not filename.lower().endswith(('.jpg', '.png')):
        continue

    image_path = os.path.join(uploads_dir, filename)
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    for face_encoding in encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)

        for i, is_match in enumerate(matches):
            if is_match:
                name = known_names[i]
                person_dir = os.path.join(output_dir, name)
                os.makedirs(person_dir, exist_ok=True)
                image_output_path = os.path.join(person_dir, filename)

                # Save copy of the image
                Image.open(image_path).save(image_output_path)
                print(f"Saved {filename} to {person_dir}")

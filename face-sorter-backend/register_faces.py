import face_recognition
import os
import pickle

KNOWN_FACES_DIR = "reference_faces"
ENCODINGS_FILE = "encodings.pkl"

encodings = []
names = []

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(KNOWN_FACES_DIR, filename)
        print(f"Processing {filename}...")

        image = face_recognition.load_image_file(image_path)
        face_encs = face_recognition.face_encodings(image)

        if face_encs:
            encodings.append(face_encs[0])
            names.append(os.path.splitext(filename)[0])
        else:
            print(f"❌ No face found in {filename}")

with open(ENCODINGS_FILE, "wb") as f:
    pickle.dump((encodings, names), f)

print(f"✅ Encoded {len(encodings)} faces.")
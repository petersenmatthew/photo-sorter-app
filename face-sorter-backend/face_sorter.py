import face_recognition
import os
import pickle
from PIL import Image

def register_faces(reference_dir="reference_faces", encodings_file="encodings.pkl"):
    encodings = []
    names = []

    for filename in os.listdir(reference_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(reference_dir, filename)
            print(f"Processing {filename}...")

            image = face_recognition.load_image_file(image_path)
            face_encs = face_recognition.face_encodings(image)

            if face_encs:
                encodings.append(face_encs[0])
                names.append(os.path.splitext(filename)[0])
            else:
                print(f"❌ No face found in {filename}")

    with open(encodings_file, "wb") as f:
        pickle.dump((encodings, names), f)

    print(f"✅ Encoded {len(encodings)} faces.")

def sort_photos(reference_dir, group_dir, output_dir="output", encodings_file="encodings.pkl"):
    # Run register_faces first to update encodings (optional)
    # Or assume encodings_file already exists

    # Load known encodings
    with open(encodings_file, "rb") as f:
        known_encodings, known_names = pickle.load(f)

    os.makedirs(output_dir, exist_ok=True)

    # Process each uploaded photo
    for filename in os.listdir(group_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        image_path = os.path.join(group_dir, filename)
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

    return {"message": "Sorting complete."}

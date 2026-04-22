import cv2
import numpy as np
import json
from app.models.db import get_all_users
import logging
import face_recognition

logger = logging.getLogger(__name__)


def get_face_embedding(img):
    try:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(img_rgb)

        if len(face_locations) == 0:
            return None, "No face detected"

        if len(face_locations) > 1:
            return None, "Multiple faces detected"

        encodings = face_recognition.face_encodings(img_rgb, face_locations)

        if not encodings:
            return None, "Face encoding failed"

        return encodings[0], None

    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        return None, str(e)


def recognize_user(embedding, tolerance=0.6):
    try:
        users = get_all_users()

        known_encodings = []
        user_data = []

        for u in users:
            if not u.get("embedding"):
                continue

            try:
                enc = np.array(json.loads(u["embedding"]))
                known_encodings.append(enc)
                user_data.append(u)
            except:
                continue

        if not known_encodings:
            return None, None

        matches = face_recognition.compare_faces(known_encodings, embedding, tolerance)
        distances = face_recognition.face_distance(known_encodings, embedding)

        best_match_index = np.argmin(distances)

        if matches[best_match_index]:
            user = user_data[best_match_index]
            return user["id"], user.get("full_name") or user.get("username")

        return None, None

    except Exception as e:
        logger.error(f"Recognition error: {str(e)}")
        return None, None


def check_duplicate_face(embedding, tolerance=0.5):
    user_id, name = recognize_user(embedding, tolerance)
    if user_id:
        return True, name
    return False, None
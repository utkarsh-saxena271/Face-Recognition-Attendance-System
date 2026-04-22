import cv2
import numpy as np
import json
from app.models.db import get_all_users
import logging
from deepface import DeepFace
import os

logger = logging.getLogger(__name__)

# 🔥 reduce tensorflow logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# 🔥 preload model (important for speed)
DeepFace.build_model("SFace")


def get_face_embedding(img):
    try:
        # ⚡ resize with better ratio (more stable than 320x240)
        img = cv2.resize(img, (224, 224))

        # 🔥 get embedding
        result = DeepFace.represent(
            img_path=img,
            model_name="SFace",
            enforce_detection=False,
            detector_backend="opencv"  # faster + stable
        )

        # ❌ no face
        if not result or len(result) == 0:
            return None, "No face detected. Ensure proper lighting."

        # ❌ multiple faces
        if len(result) > 1:
            return None, "Multiple faces detected. Only one face allowed."

        embedding = np.array(result[0]["embedding"])
        return embedding, None

    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        return None, str(e)


def recognize_user(embedding, threshold=13):
    try:
        users = get_all_users()

        best_match = None
        best_distance = float("inf")

        for u in users:
            if not u.get("embedding"):
                continue

            try:
                stored = np.array(json.loads(u["embedding"]))
            except:
                continue

            # 🔥 compute distance
            distance = np.linalg.norm(stored - embedding)

            # 🧠 DEBUG (keep this while testing)
            print(f"User: {u.get('username')} | Distance: {distance:.2f}")

            # 🔍 best match selection
            if distance < best_distance:
                best_distance = distance
                best_match = u

        # ✅ final decision
        if best_match and best_distance < threshold:
            print(f"✅ MATCH FOUND: {best_match.get('username')} (Distance: {best_distance:.2f})")
            return best_match["id"], best_match.get("full_name") or best_match.get("username")

        print(f"❌ NO MATCH (Best Distance: {best_distance:.2f})")
        return None, None

    except Exception as e:
        logger.error(f"Recognition error: {str(e)}")
        return None, None


def check_duplicate_face(embedding, threshold=13):
    user_id, name = recognize_user(embedding, threshold)
    if user_id:
        return True, name
    return False, None
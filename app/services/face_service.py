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


# ============================================
# FACE EMBEDDING
# ============================================

def get_face_embedding(img):
    try:
        if img is None:
            return None, "Image not loaded"

        result = DeepFace.represent(
            img_path=img,
            model_name="Facenet",
            enforce_detection=True,
            detector_backend="opencv"
        )

        if isinstance(result, dict):
            result = [result]

        if not result:
            return None, "No face detected"

        if len(result) > 1:
            return None, "Multiple faces detected"

        embedding = np.array(result[0]["embedding"])

        norm = np.linalg.norm(embedding)
        if norm == 0:
            return None, "Invalid embedding"

        embedding = embedding / norm

        return embedding, None

    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        return None, str(e)


# ============================================
# FACE RECOGNITION
# ============================================

def recognize_user(embedding, threshold=0.7):
    try:
        if embedding is None:
            return None, None

        users = get_all_users()

        best_match = None
        best_distance = float("inf")

        for u in users:
            if not u.get("embedding"):
                continue

            try:
                stored = np.array(json.loads(u["embedding"]))

                norm = np.linalg.norm(stored)
                if norm == 0:
                    continue

                stored = stored / norm

            except:
                continue

            distance = np.linalg.norm(stored - embedding)

            print(f"User: {u.get('username')} | Distance: {distance:.4f}")

            if distance < best_distance:
                best_distance = distance
                best_match = u

        if best_match and best_distance < threshold:
            print(f"✅ MATCH: {best_match.get('username')} ({best_distance:.4f})")
            return best_match["id"], best_match.get("full_name") or best_match.get("username")

        print(f"❌ NO MATCH ({best_distance:.4f})")
        return None, None

    except Exception as e:
        logger.error(f"Recognition error: {str(e)}")
        return None, None


# ============================================
# DUPLICATE CHECK
# ============================================

def check_duplicate_face(embedding, threshold=0.7):
    user_id, name = recognize_user(embedding, threshold)

    if user_id:
        return True, name

    return False, None
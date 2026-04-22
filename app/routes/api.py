from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import traceback
import logging
import json
from datetime import datetime, timezone, timedelta   # ✅ added timedelta

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger('app')

from app.models.db import (
    get_user_by_id, get_attendance_by_user, mark_attendance, get_all_users
)
from app.services.email_service import EmailService

email_service = EmailService()

# ✅ IST TIMEZONE (ADDED)
IST = timezone(timedelta(hours=5, minutes=30))


def get_face_recognition_modules():
    try:
        from app.utils.helpers import base64_to_cv2
        from app.services.face_service import get_face_embedding, recognize_user, check_duplicate_face
        return (base64_to_cv2, get_face_embedding, recognize_user, check_duplicate_face, True)
    except BaseException as e:
        logger.warning(f"Face recognition not available: {e}")
        return (None, None, None, None, False)


@api_bp.route('/register-user', methods=['POST'])
@login_required
def register():
    try:
        logger.info(f"Face registration request started for user_id={current_user.id}")
        base64_to_cv2, get_face_embedding, recognize_user_fn, check_duplicate_face, available = get_face_recognition_modules()

        if not available:
            return jsonify({'success': False, 'message': 'Face recognition not available yet. Please try again later.'}), 503

        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'Invalid data provided.'}), 400

        image_b64 = data.get('image', '')

        if not image_b64:
            return jsonify({'success': False, 'message': 'Image is required.'}), 400

        img = base64_to_cv2(image_b64)
        if img is None:
            return jsonify({'success': False, 'message': 'Invalid image format.'}), 400

        embedding, err = get_face_embedding(img)
        if err:
            return jsonify({'success': False, 'message': err}), 400

        is_dup, dup_name = check_duplicate_face(embedding)
        if is_dup:
            return jsonify({'success': False, 'message': f'This face is already registered to {dup_name}.'}), 400

        user_data = get_user_by_id(current_user.id)
        if not user_data:
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        try:
            from app.models.db import get_db_connection
            conn = get_db_connection()
            c = conn.cursor()

            embedding_json = json.dumps(embedding.tolist())
            c.execute('UPDATE users SET embedding = ? WHERE id = ?', (embedding_json, current_user.id))

            conn.commit()
            conn.close()

        except Exception as db_err:
            logger.error(f"Database error saving embedding: {str(db_err)}")
            return jsonify({'success': False, 'message': 'Failed to save face data.'}), 500

        return jsonify({
            'success': True,
            'message': f"Face registered successfully for {user_data['full_name']}!"
        })

    except Exception as e:
        logger.error(f"Error registering face: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/recognize-face', methods=['POST'])
def recognize():
    try:
        # 🔥 FIX: UTC → IST
        recognition_time = datetime.now(IST)

        base64_to_cv2, get_face_embedding, recognize_user_fn, check_duplicate_face, available = get_face_recognition_modules()

        if not available:
            return jsonify({'success': False, 'message': 'Face recognition not available. Please contact administrator.'}), 503

        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'Invalid data provided.'}), 400

        image_b64 = data.get('image', '')

        if not image_b64:
            return jsonify({'success': False, 'message': 'Image is required.'}), 400

        img = base64_to_cv2(image_b64)
        if img is None:
            return jsonify({'success': False, 'message': 'Invalid image format.'}), 400

        embedding, err = get_face_embedding(img)
        if err:
            return jsonify({'success': False, 'message': err}), 400

        user_id, name = recognize_user_fn(embedding)

        if user_id:
            user_data = get_user_by_id(user_id)
            if not user_data:
                return jsonify({'success': True, 'found': False, 'message': 'User data not found.'}), 200

            marked, status = mark_attendance(user_id, recognition_time)

            if marked:
                logger.info(f"Attendance marked for user {user_data['username']}")

                # ✅ IST formatted time
                attendance_time = recognition_time.strftime('%Y-%m-%d %H:%M:%S')

                return jsonify({
                    'success': True,
                    'found': True,
                    'user_id': user_id,
                    'user_name': user_data['full_name'],
                    'user_email': user_data['email'], 
                    'status': status,
                    'marked_at': attendance_time,
                    'message': f"{user_data['full_name']} marked at {attendance_time} IST"
                })      
            else:
                return jsonify({
                    'success': True,
                    'found': True,
                    'user_id': user_id,
                    'user_name': user_data['full_name'],
                    'status': 'duplicate',
                    'message': "Attendance already marked"
                })

        return jsonify({'success': True, 'found': False, 'message': 'Unknown face'})

    except Exception as e:
        logger.error(f"Error in face recognition: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/attendance', methods=['GET'])
@login_required
def attendance():
    try:
        records = get_attendance_by_user(current_user.id, limit=50)
        user_data = get_user_by_id(current_user.id)

        display_name = user_data.get('full_name') if user_data else None

        res = [{
            'date': r['date'],
            'name': display_name,
            'time': r['time_in'],
            'time_in': r['time_in'],
            'time_out': r.get('time_out'),
            'marked_at': f"{r['date']}T{r['time_in']}",
            'status': r.get('status', 'present')
        } for r in records]

        return jsonify({'success': True, 'data': res})

    except Exception as e:
        logger.error(f"Error retrieving attendance: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = get_all_users()
        res = [{'id': u['id'], 'name': u.get('full_name', u.get('name'))} for u in users]
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
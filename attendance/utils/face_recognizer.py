import pickle
from django.utils import timezone
from django.core.files.base import ContentFile
from django.conf import settings
import time
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
import face_recognition as frg
import cv2
import numpy as np
from attendance.models import Employee, Attendance
import logging
import asyncio
import os

from attendance.utils.my_cache import set_employees

logger = logging.getLogger(__name__)

# Track last sent email per face
last_email_sent = {}
unknown_faces_file = 'unknown_faces.pkl'  # File to store unknown faces
unknown_faces = {}  # Track unknown face encodings and their assigned IDs

def save_unknown_faces_locally():
    with open(unknown_faces_file, 'wb') as f:
        pickle.dump(unknown_faces, f)
    # logger.info("Unknown faces saved locally")

def load_unknown_faces():
    global unknown_faces
    if os.path.exists(unknown_faces_file):
        with open(unknown_faces_file, 'rb') as f:
            unknown_faces = pickle.load(f)
        # logger.info("Unknown faces loaded")
    else:
        logger.info("No unknown faces file found. Starting fresh.")

def record_attendance(employee, delta_minutes=5):
    last_attendance = Attendance.objects.filter(employee=employee).order_by('-timestamp').first()
    if last_attendance and (timezone.now() - last_attendance.timestamp).total_seconds() < delta_minutes * 60:
        return False
    Attendance.objects.create(employee=employee)
    return True

def save_unknown_face(frame, face_id):
    ret, jpeg = cv2.imencode('.jpg', frame)
    photo = ContentFile(jpeg.tobytes())
    filename = f"inconnu{face_id}.jpg"
    photo.name = filename
    return photo

def store_known_faces_locally():
    employees = Employee.objects.all()
    known_face_encodings = []
    known_face_ids = []
    for employee in employees:
        image = frg.load_image_file(employee.photo.path)
        encoding = frg.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_ids.append(employee.id)
    logger.info("Démarrage de l'encodage")

    with open('known_faces.pkl', 'wb') as f:
        pickle.dump([known_face_encodings, known_face_ids], f)
    logger.info("Encodage terminé")

def load_known_faces():
    with open('known_faces.pkl', 'rb') as f:
        known_face_encodings, known_face_ids = pickle.load(f)

    return known_face_encodings, known_face_ids

async def send_unknown_face_email(unknown_face_photo, face_id):
    await asyncio.sleep(1)  
    subject = f"⚠ Intrusion détectée | {datetime.now().strftime('%d/%m/%Y')}"
    message = 'Un intrus a été détecté . veuillez trouver ci-attaché son photo.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['devschoolsup@gmail.com']

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.attach(f"inconnu{face_id}.jpg", unknown_face_photo.read(), 'image/jpeg')
        email.send()
        logger.info("Email sent for unknown face detection.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def recognize_face(frame, known_face_encodings, known_face_ids, threshold=0.6):
    cam_small = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    cam_face_locations = frg.face_locations(cam_small)
    cam_face_encodings = frg.face_encodings(cam_small, cam_face_locations)

    known_employees = []
    current_time = time.time()
    unique_face_counter = len(unknown_faces)  # Initialize with the count of already tracked unknown faces

    for locations, face_encodings_to_check in zip(cam_face_locations, cam_face_encodings):
        name = "Inconnu"
        top, right, bottom, left = locations
        top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
        face_distances = frg.face_distance(known_face_encodings, face_encodings_to_check)
        best_match_index = np.argmin(face_distances)
        if face_distances[best_match_index] < threshold:
            id = known_face_ids[best_match_index]
            employee = Employee.objects.get(id=id)
            name = employee.get_full_name()
            known_employees.append(employee)
            record_attendance(employee)
            color = (0, 255, 0)  # Green
            set_employees(known_employees)
        else:
            # Check if the face encoding has been seen before
            matched_face_id = None
            for stored_encoding, face_id in unknown_faces.items():
                if np.linalg.norm(stored_encoding - face_encodings_to_check) < threshold:
                    matched_face_id = face_id
                    break

            if matched_face_id is None:
                unique_face_counter += 1
                matched_face_id = f"{datetime.now().strftime('%Y%m%d')}_{unique_face_counter}"
                unknown_faces[tuple(face_encodings_to_check)] = matched_face_id

            if matched_face_id not in last_email_sent or current_time - last_email_sent[matched_face_id] > 86400:
                logger.critical(f"Email sent: {matched_face_id}")
                unknown_image = save_unknown_face(frame, matched_face_id)
                asyncio.run(send_unknown_face_email(unknown_image, matched_face_id))
                last_email_sent[matched_face_id] = current_time

            color = (0, 0, 255)  # Red
            name = f"Inconnu{matched_face_id}"

        cv2.rectangle(frame, (left, top), (right, bottom), color, 1)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, color, 2)

    # Save unknown faces to file after each recognition cycle
    save_unknown_faces_locally()

    return frame, known_employees

# Load known and unknown faces on startup
load_known_faces()
load_unknown_faces()

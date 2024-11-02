import threading
import cv2
from ..utils.face_recognizer import recognize_face, load_known_faces
import logging

logger = logging.getLogger(__name__)


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(3, 640)
        self.video.set(4, 480)
        if not self.video.isOpened():
            raise ValueError("Unable to open video source")
        logger.info("Video source opened successfully")

        self.known_face_encodings, self.known_face_ids = load_known_faces()
        logger.info("Known faces loaded")

    def __del__(self):
        self.video.release()
        logger.info("Video source released")

    def get_frame(self, recognition_enabled=False):
        ret, frame = self.video.read()
        if not ret:
            logger.warning("⚠️ No frame detected")
            return None
        if recognition_enabled:
            frame, names = recognize_face(frame, self.known_face_encodings, self.known_face_ids)

        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            return jpeg.tobytes()
        else:
            logger.error("⚠️ Failed to encode frame")
            return None

import face_recognition as frg
import pickle
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Employee
from .utils.face_recognizer import load_known_faces

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Employee)
@receiver(post_delete, sender=Employee)
def update_known_faces(sender, instance, **kwargs):
    known_face_encodings, known_face_ids = load_known_faces()
    if kwargs.get('created'):
        image = frg.load_image_file(instance.photo.path)
        encoding = frg.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_ids.append(instance.id)
        logger.info(f'Employee {instance.get_full_name()} est ajouté.')
    else:
        if instance.id in known_face_ids:
            index = known_face_ids.index(instance.id)
            known_face_encodings.pop(index)
            known_face_ids.pop(index)
        logger.info(f'Employee {instance.get_full_name()} est supprimé.')

    logger.info("Démarrer: Mise à jour des encodages des visages connus")
    with open('known_faces.pkl', 'wb') as f:
        pickle.dump([known_face_encodings, known_face_ids], f)

    logger.info("Terminer: Mise à jour des encodages des visages connus")

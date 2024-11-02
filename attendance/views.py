from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from attendance.utils.my_cache import set_webcam_status, get_webcam_status, set_recognition_enabled, \
    get_recognition_enabled, get_employees
from attendance.utils.video_camera import VideoCamera

import json
import logging

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'attendance/index.html')


def accueil(request):
    return render(request, 'attendance/accueil.html')


@csrf_exempt
def toggle_camera(request):
    try:
        data = json.loads(request.body)
        is_camera_on = data.get('isCameraOn', False)
        logger.debug(f"is_camera_on: {is_camera_on}")
        set_webcam_status(is_camera_on)
        return JsonResponse({"success": True, "isCameraOn": is_camera_on})
    except Exception as e:
        logger.error(f"Error in toggle_camera: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def toggle_recognition(request):
    try:
        data = json.loads(request.body)
        recognition_enabled = data.get('recognitionEnabled', False)
        logger.debug(f"recognition_enabled: {recognition_enabled}")
        set_recognition_enabled(recognition_enabled)
        return JsonResponse({"success": True, "recognitionEnabled": recognition_enabled})
    except Exception as e:
        logger.error(f"Error in toggle_recognition: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)})


def gen(camera):
    try:
        while True:
            frame = camera.get_frame(get_recognition_enabled())
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                logger.warning("No frame to yield")
                break
    except Exception as e:
        logger.error(f"Error in gen: {str(e)}")


def video_feed(request):
    if not get_webcam_status():
        return JsonResponse({"success": False, "message": "Camera is not active"}, status=403)
    return StreamingHttpResponse(gen(VideoCamera()), content_type='multipart/x-mixed-replace; boundary=frame')


@csrf_exempt
def recognize_and_register(request):
    # logger.debug(f"get_employees(): {get_employees()}")
    if len(get_employees()) == 0:
        return JsonResponse({"success": False, "message": "No employee found"}, status=404)
    data = [employee.to_dict() for employee in get_employees()]
    # logger.debug(f"data: {data}")
    return JsonResponse({"success": True, "employees": data}, status=200)

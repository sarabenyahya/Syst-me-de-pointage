from django.core.cache import cache

# Cache keys
CAMERA_STATUS_KEY = 'webcam_status'
RECOGNITION_ENABLED_KEY = 'recognition_enabled'
EMPLOYEES = None

# Initialize cache with default values if not set
if cache.get(CAMERA_STATUS_KEY) is None:
    cache.set(CAMERA_STATUS_KEY, False)
if cache.get(RECOGNITION_ENABLED_KEY) is None:
    cache.set(RECOGNITION_ENABLED_KEY, False)

# if cache.get(EMPLOYEES) is None:
#     cache.set(EMPLOYEES, [])
cache.set(EMPLOYEES, [])

def get_webcam_status():
    return cache.get(CAMERA_STATUS_KEY)


def set_webcam_status(status):
    cache.set(CAMERA_STATUS_KEY, status)


def get_recognition_enabled():
    return cache.get(RECOGNITION_ENABLED_KEY)


def set_recognition_enabled(status):
    cache.set(RECOGNITION_ENABLED_KEY, status)


def set_employees(employees):
    cache.set(EMPLOYEES, employees)


def get_employees():
    return cache.get(EMPLOYEES)

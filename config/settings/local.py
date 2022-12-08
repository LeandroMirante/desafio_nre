from .base import *
import os

STATIC_URL = "static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "static.uploads")

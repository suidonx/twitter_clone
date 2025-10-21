from .base import *

DEBUG = False

ALLOWED_HOSTS = [".herokuapp.com"]

INSTALLED_APPS += [
    "cloudinary",
    "cloudinary_storage",
]

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

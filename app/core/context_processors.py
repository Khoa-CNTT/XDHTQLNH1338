# context_processors.py


def cloudinary_settings(request):
    from django.conf import settings
    return {
        "cloud_name": settings.CLOUDINARY_STORAGE["CLOUD_NAME"],
    }

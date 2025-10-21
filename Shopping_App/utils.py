import cloudinary
import cloudinary.uploader
from django.core.exceptions import ValidationError
# import random
# from django.utils import timezone
# from datetime import timedelta

def upload_file_to_cloudinary(file, folder="uploads", resource_type="auto"):
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True,
            overwrite=False
        )
        return result.get("secure_url")
    except Exception as e:
        raise ValidationError(f"Cloudinary upload failed: {str(e)}")
    
# def generate_otp():
#     return str(random.randint(100000, 999999))

# def set_user_otp(user):
#     otp = generate_otp()
#     user.otp_code = otp
#     user.otp_expiry = timezone.now() + timedelta(minutes=10)
#     user.save()
#     return otp
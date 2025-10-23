import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# Paths
LOCAL_IMAGE_FOLDER = r"C:\Users\user\Desktop\Ecommerce\media\img"
CLOUDINARY_FOLDER = "ecommerce_media"
VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')

# Upload all valid images recursively
for root, _, files in os.walk(LOCAL_IMAGE_FOLDER):
    for filename in files:
        if filename.lower().endswith(VALID_EXTENSIONS):
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, LOCAL_IMAGE_FOLDER)
            cloudinary_path = os.path.join(CLOUDINARY_FOLDER, os.path.dirname(relative_path)).replace("\\", "/")

            try:
                print(f"🔼 Uploading: {relative_path}...")
                result = cloudinary.uploader.upload(
                    local_path,
                    folder=cloudinary_path,
                    use_filename=True,
                    unique_filename=False
                )
                print(f"✅ Uploaded: {filename}")
                print(f"📸 URL: {result['secure_url']}\n")
            except Exception as e:
                print(f"❌ Failed to upload {filename}: {e}")

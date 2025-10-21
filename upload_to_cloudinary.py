import os
import cloudinary
import cloudinary.uploader

# 🔐 Cloudinary configuration (replace with your actual credentials)
cloudinary.config( 
  cloud_name = 'dorjc6aib',        # e.g. 'mycloud123'
  api_key = '713263282653134',
  api_secret = 'LNsHUQ59xrnhyOgh_pdx3tm9Qq8'
)

# 📂 Correct path to your images
LOCAL_IMAGE_FOLDER = r"C:\Users\user\Desktop\Ecommerce\media\img"
CLOUDINARY_FOLDER = "ecommerce_media"  # You can rename this

# ✅ Upload all image files from the folder
for filename in os.listdir(LOCAL_IMAGE_FOLDER):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
        file_path = os.path.join(LOCAL_IMAGE_FOLDER, filename)
        try:
            print(f"Uploading {filename}...")
            result = cloudinary.uploader.upload(
                file_path,
                folder=CLOUDINARY_FOLDER,
                use_filename=True,
                unique_filename=False
            )
            print(f"✅ Uploaded: {filename}")
            print(f"🌐 URL: {result['secure_url']}\n")
        except Exception as e:
            print(f"❌ Failed to upload {filename}: {e}")

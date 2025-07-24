import cloudinary
import cloudinary.uploader
from src.config import Config

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

def upload_image(file, folder="estoque"):
    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type="image",
        quality="auto:eco"
    )
    return result['secure_url']
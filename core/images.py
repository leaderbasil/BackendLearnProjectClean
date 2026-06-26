from dotenv import load_dotenv
from imagekit import ImageKit
import os

load_dotenv()
imagekit = ImageKit(
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    base_url=os.getenv("IMAGEKIT_BASE_URL")
)
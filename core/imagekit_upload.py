import requests
import base64
import logging
from fastapi import UploadFile, HTTPException, status
from core.config import settings

logger = logging.getLogger(__name__)


class ImageKitUploader:
    def __init__(self):
        self.private_key = settings.IMAGEKIT_PRIVATE_KEY
        self.url_endpoint = settings.IMAGEKIT_URL_ENDPOINT
        self.upload_url = "https://upload.imagekit.io/api/v1/files/upload"
    async def upload(self, file: UploadFile, folder: str = "/blogs") -> str:
        try:
            file_content = await file.read()
            auth_header = base64.b64encode(
                f"{self.private_key}:".encode()
            ).decode()

            response = requests.post(
                self.upload_url,
                headers={"Authorization": f"Basic {auth_header}"},
                files={"file": (file.filename, file_content)},
                data={
                    "fileName": file.filename,
                    "folder": folder,
                    "useUniqueFileName": "true",
                }
            )

            if response.status_code != 200:
                logger.error(f"Upload failed: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.json().get("message", "Upload failed")
                )

            return response.json()["url"]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Upload error: {str(e)}"
            )
imagekit_uploader = ImageKitUploader()
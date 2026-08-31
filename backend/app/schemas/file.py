from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_name: str
    path: str

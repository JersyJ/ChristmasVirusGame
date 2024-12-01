from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID

class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass

class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str


class UserCreateRequest(BaseRequest):
    email: EmailStr
    password: str
    
class DeviceCreateRequest(BaseRequest):
    uuid : UUID = Field(..., description="The UUID of the device", examples=["00000000-0000-0000-0000-080027c3ff56"])
    ip_address: str = Field(..., description="The IP address of the device", min_length=1, max_length=45, examples=["10.0.2.15"])
    status: str = Field(..., description="The status of the device", min_length=1, max_length=20, examples=["starting"])
    encryption_key: str = Field(..., description="The encryption key of the device", min_length=1, max_length=256, examples=["WuGyrbREjFXB4Z9HcWnrUjhMBYyX-a7JAONr4OrlN1M="])
    
class FileCreateRequest(BaseRequest):
    file_path: str = Field(..., description="The path of the file", min_length=1, max_length=32767, examples=["C:\\Users\\User\\Desktop\\data\\F1\\aaa1 - Copy.txt"])
    original_content: str = Field(..., description="The original content of the file", min_length=0, max_length=2097152, examples=["Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vulputate mollis velit, in placerat magna viverra in. Curabitur luctus justo vel sapien"])

class DeviceSubmitRequest(BaseRequest):
    uuid : UUID = Field(..., description="The UUID of the device", examples=["00000000-0000-0000-0000-080027c3ff56"])
    ip_address: str = Field(..., description="The IP address of the device", min_length=1, max_length=45, examples=["10.0.2.15"])
    status: str = Field(..., description="The status of the device", min_length=1, max_length=20, examples=["running", "completed"])
    file: FileCreateRequest | None = Field(None, description="The file submitted with the status", examples=[{"file_path": "C:\\Users\\User\\Desktop\\data\\F1\\aaa1 - Copy.txt", "original_content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vulputate mollis velit, in placerat magna viverra in. Curabitur luctus justo vel sapien"}])

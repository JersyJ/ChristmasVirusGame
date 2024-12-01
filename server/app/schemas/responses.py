from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID

class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AccessTokenResponse(BaseResponse):
    token_type: str = "Bearer"
    access_token: str
    expires_at: int
    refresh_token: str
    refresh_token_expires_at: int


class UserResponse(BaseResponse):
    user_id: str
    email: EmailStr
    
class DeviceCreateResponse(BaseResponse):
    id: int = Field(..., description="The ID of the device", examples=[1])
    
class DeviceSubmitResponse(BaseResponse):
    id: int = Field(..., description="The ID of the device", examples=[1])
    
class DeviceResponse(BaseResponse):
    id: int = Field(..., description="The ID of the device", examples=[1])
    uuid: UUID = Field(..., description="The UUID of the device", examples=["00000000-0000-0000-0000-080027c3ff56"])
    
class DeviceStatusResponse(BaseResponse):
    id: int = Field(..., description="The ID of the status", examples=[1])
    ip_address: str = Field(..., description="The IP address of the device", min_length=1, max_length=45, examples=["10.0.2.15"])
    status: str = Field(..., description="The status of the device", min_length=1, max_length=20, examples=["starting", "running", "completed"])
    file_id: int | None = Field(description="The ID of the file", examples=[1])

class FileResponse(BaseResponse):
    id: int = Field(..., description="The ID of the device", examples=[1])
    file_path: str = Field(..., description="The path of the file", min_length=1, max_length=32767, examples=["C:\\Users\\User\\Desktop\\data\\F1\\aaa1 - Copy.txt"])
    original_content: str = Field(..., description="The original content of the file", min_length=0, max_length=2097152, examples=["Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vulputate mollis velit, in placerat magna viverra in. Curabitur luctus justo vel sapien"])

class DeviceWithStatusResponse(BaseResponse):
    id: int = Field(..., description="The ID of the device", examples=[1])
    uuid: UUID = Field(..., description="The UUID of the device", examples=["00000000-0000-0000-0000-080027c3ff56"])
    statuses: list[DeviceStatusResponse | None] = Field(description="The statuses of the device")
    
class DeviceFilesResponse(BaseResponse):
    id: int = Field(..., description="The ID of the device", examples=[1])
    uuid: UUID = Field(..., description="The UUID of the device", examples=["00000000-0000-0000-0000-080027c3ff56"])
    files: list[FileResponse | None]  = Field(description="The files of the device")
    
    


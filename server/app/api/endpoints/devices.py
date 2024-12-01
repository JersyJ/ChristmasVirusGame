from typing import Annotated

from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api import deps
from app.schemas.requests import DeviceCreateRequest, DeviceSubmitRequest
from app.schemas.responses import DeviceCreateResponse, DeviceSubmitResponse, DeviceResponse, DeviceFilesResponse, DeviceWithStatusResponse
from app.models import Device, DeviceStatus, File
from sqlalchemy import select

router = APIRouter()


@router.post(
    "",
    response_model=DeviceCreateResponse,
    description="Create and save a new device",
    operation_id="create_device",
    status_code=status.HTTP_201_CREATED,
)
async def create_device(
    data: DeviceCreateRequest, session: AsyncSession = Depends(deps.get_session)
) -> DeviceCreateResponse:
    """
    Create and save a new Device.
    :param data: DeviceCreateRequest
    :param session: AsyncSession
    :return: DeviceResponse
    """
    device = await session.scalar(select(Device).where(Device.uuid == data.uuid))
    if device:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device with UUID {data.uuid} already exist",
        )
    
    new_device = Device(uuid = data.uuid)
    
    new_device_status = DeviceStatus(status = data.status, ip_address = data.ip_address)
    new_device.statuses.append(new_device_status)
    session.add(new_device)
    await session.commit()
    return DeviceCreateResponse.model_validate(new_device)

@router.post(
    "/submit",
    response_model=DeviceSubmitResponse,
    description="Submit status of a device.",
    operation_id="submit_status_of_device",
    status_code=status.HTTP_200_OK,
)
async def submit_device(data: DeviceSubmitRequest, session: AsyncSession = Depends(deps.get_session)
) -> DeviceSubmitResponse:
    """
    Submit status of a device.
    :param Device_id: int
    :param session: AsyncSession
    :return: DeviceSubmitResponse
    """
    device = await session.scalar(select(Device).where(Device.uuid == data.uuid))
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with UUID {data.uuid} does not exist",
        )
    if data.file:
        file = File(file_path = data.file.file_path, original_content = data.file.original_content)
        device.files.append(file)

    new_device_status = DeviceStatus(status = data.status, ip_address = data.ip_address, file = file if data.file else None)
    device.statuses.append(new_device_status)
    session.add(device)
    await session.commit()
    return DeviceSubmitResponse.model_validate(device)

@router.get(
    "/{device_uuid:str}",
    response_model=DeviceResponse,
    description="Get existing device by UUID.",
    operation_id="get_device_by_uuid",
    # dependencies=[Depends(deps.get_current_user)],
    status_code=status.HTTP_200_OK,
)
async def get_device_by_uuid(
    device_uuid: Annotated[UUID, Path(..., description="The UUID of the device")], session: AsyncSession = Depends(deps.get_session)
) -> DeviceResponse:
    """
    Get existing device by UUID.
    :param device_uuid: UUID
    :param session: AsyncSession
    :return: DeviceResponse
    """

    device = await session.scalar(select(Device).where(Device.uuid == device_uuid))
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with this UUID {device_uuid} does not exist",
        )
    return DeviceResponse.model_validate(device)


@router.get(
    "",
    response_model=list[DeviceResponse],
    description="Get all existing Devices.",
    operation_id="get_all_Devices",
    # dependencies=[Depends(deps.get_current_user)],
    status_code=status.HTTP_200_OK,
)
async def get_all_devices(session: AsyncSession = Depends(deps.get_session)) -> list[DeviceResponse | None]:
    """
    Get all Devices
    :param session: AsyncSession
    :return: list[DeviceResponse]
    """
    devices = await session.scalars(select(Device).order_by(Device.id))
    return [DeviceResponse.model_validate(device) for device in devices]


@router.get(
    "/{device_id:int}/status",
    response_model=DeviceWithStatusResponse,
    description="Get all statuses of a device by its id.",
    operation_id="get_all_statuses_of_device",
    # dependencies=[Depends(deps.get_current_user)],
    status_code=status.HTTP_200_OK,
)
async def get_all_statuses_of_device(
    device_id: int, session: AsyncSession = Depends(deps.get_session)
) -> DeviceWithStatusResponse:
    """
    Get all statuses of a device by its id.
    :param device_id: int
    :param session: AsyncSession
    :return: DeviceWithStatusResponse
    """
    device = await session.scalar(select(Device).where(Device.id == device_id))
    return DeviceWithStatusResponse.model_validate(device)


@router.get(
    "/{device_id:int}/files",
    response_model=DeviceFilesResponse,
    description="Get all files of a device by its id.",
    operation_id="get_all_files_of_device",
    # dependencies=[Depends(deps.get_current_user)],
    status_code=status.HTTP_200_OK,
)
async def get_all_files_of_device(
    device_id: int, session: AsyncSession = Depends(deps.get_session)
) -> DeviceFilesResponse:
    """
    Get all files of a device by its id.
    :param device_id: int
    :param session: AsyncSession
    :return: DeviceFilesResponse
    """
    device = await session.scalar(select(Device).where(Device.id == device_id))
    return DeviceFilesResponse.model_validate(device)

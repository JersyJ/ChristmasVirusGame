# SQL Alchemy models declaration.
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
# mapped_column syntax from SQLAlchemy 2.0.

# https://alembic.sqlalchemy.org/en/latest/tutorial.html
# Note, it is used by alembic migrations logic, see `alembic/env.py`

# Alembic shortcuts:
# # create migration
# alembic revision --autogenerate -m "migration_name"

# # apply all migrations
# alembic upgrade head


import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Uuid,
    func,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "user_account"

    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(256), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(
        String(512), nullable=False, unique=True, index=True
    )
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_account.user_id", ondelete="CASCADE"),
    )
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

class File(Base):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"))

    file_path: Mapped[Text] = mapped_column(Text, nullable=False)
    original_content: Mapped[Text] = mapped_column(Text, nullable=False)

    device: Mapped["Device"] = relationship(back_populates="files", lazy="selectin")

class Device(Base):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    uuid: Mapped[str] = mapped_column(Uuid, nullable=False, unique=True)
    statuses: Mapped[list["DeviceStatus"] | None] = relationship(
        back_populates="device", cascade="all, delete-orphan", lazy="selectin"
    )
    files: Mapped[list[File] | None]  = relationship(back_populates="device", lazy="selectin")



class DeviceStatus(Base):
    __tablename__ = "device_status"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    ip_address: Mapped[str] = mapped_column(String(45))

    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"))
    file_id: Mapped[int | None] = mapped_column(ForeignKey("file.id"), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False)

    device: Mapped[Device] = relationship(back_populates="statuses", lazy="selectin")
    file: Mapped[File | None] = relationship(uselist=False)




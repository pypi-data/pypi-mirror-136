from typing import Optional
from sqlmodel import Field, SQLModel


class MessageRecord(SQLModel, table=True):
    """消息记录"""

    __tablename__: str = "chatrecorder_message_record"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    platform: str
    time: int
    type: str
    detail_type: str
    message_id: str
    message: str
    user_id: str
    group_id: Optional[str] = ""

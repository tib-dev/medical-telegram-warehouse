from pydantic import BaseModel
from typing import List


class TopProduct(BaseModel):
    product: str
    mention_count: int


class ChannelActivity(BaseModel):
    date: str
    message_count: int
    avg_views: float


class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    view_count: int
    message_date: str


class VisualContentStats(BaseModel):
    channel_name: str
    total_messages: int
    image_messages: int
    image_ratio: float

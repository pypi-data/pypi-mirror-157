from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class HttpMethod(Enum):
    """Методы http запроса"""
    GET = "get"
    POST = "post"
    DELETE = "delete"


class UserBalance(BaseModel):
    user_id: int
    balance: float


class PaymentUrl(BaseModel):
    message: str
    url: str


class TranslationType(Enum):
    ALL = "all"
    OUT = "out"
    IN = "in"


class Translation(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    amount: float
    commission: float
    payload: str
    created_at: datetime


class SendCoins(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    amount: float
    commission: float
    payload: str
    created_at: datetime


class SetCallback(BaseModel):
    callback_url: str
    callback_secret: str


class DeleteCallback(BaseModel):
    response: str

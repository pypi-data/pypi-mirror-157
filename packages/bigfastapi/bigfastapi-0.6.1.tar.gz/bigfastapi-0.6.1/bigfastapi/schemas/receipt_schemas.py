import datetime
from typing import Optional, List
from pydantic import BaseModel,EmailStr


class Receipt(BaseModel):
    id: Optional[str]
    organization_id: Optional[str]
    sender_email: Optional[str]
    message: Optional[str]
    subject: Optional[str]
    recipient: Optional[str]
    is_deleted: Optional[bool]
    file_id: Optional[str]

    class Config:
        orm_mode = True

class atrributes(Receipt):
    recipient: List[EmailStr] = []

class DeleteSelectedReceipts(BaseModel):
    organization_id: str
    receipt_id_list: list

class SendReceiptResponse(BaseModel):
    message: str
    data: Receipt

class ReceiptsResponse(BaseModel):
    page: int
    size: int
    total: int
    items: List[Receipt]
    previous_page: Optional[str]
    next_page: Optional[str]

class FetchReceiptsResponse(BaseModel):
    data: ReceiptsResponse

class SingleReceiptResponse(BaseModel):
    data: Receipt
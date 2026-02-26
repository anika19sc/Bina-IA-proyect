from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Document Schemas
class DocumentBase(BaseModel):
    filename: str

class DocumentCreate(DocumentBase):
    file_path: str
    case_id: Optional[int] = None

class Document(DocumentBase):
    id: int
    upload_date: datetime
    case_id: Optional[int]

    class Config:
        from_attributes = True

# Case Schemas
class CaseBase(BaseModel):
    title: str
    description: Optional[str] = None

class CaseCreate(CaseBase):
    pass

class Case(CaseBase):
    id: int
    created_at: datetime
    documents: List[Document] = []


    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    sender: str
    content: str

class MessageCreate(MessageBase):
    case_id: int

class Message(MessageBase):
    id: int
    timestamp: datetime
    case_id: int

    class Config:
        from_attributes = True

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from pgvector.sqlalchemy import Vector

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1) # 1: Active, 0: Inactive
    role = Column(Integer, default=1) # 0: SuperAdmin, 1: OrgAdmin, 2: OrgEditor
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    organization = relationship("Organization", back_populates="users")

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True) # e.g., "Familia Pérez"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    organization = relationship("Organization", back_populates="cases")
    
    documents = relationship("Document", back_populates="case")
    messages = relationship("Message", back_populates="case")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String) # 'user' or 'ai'
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    case_id = Column(Integer, ForeignKey("cases.id"))

    case = relationship("Case", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String) # Path to encrypted file
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    
    # Vector embedding for semantic search (Gemini text-embedding-004 uses 768 dimensions)
    embedding = Column(Vector(768))

    # Extracted text from OCR (Hybrid: PyMuPDF or Google Cloud Vision)
    extracted_text = Column(Text, nullable=True)

    case = relationship("Case", back_populates="documents")

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Integer, default=1)

    users = relationship("User", back_populates="organization")
    cases = relationship("Case", back_populates="organization")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True) 
    user_type = Column(String, default="System") 
    action = Column(String) 
    details = Column(Text, nullable=True)
    ip_address = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

# Add relationships to existing models
# We need to monkey-patch or redefine them if we can't edit in-place easily, 
# but here I am replacing the whole file content effectively by editing the class definitions if I could,
# but since I am using replace_file_content on chunks, I need to be careful.

# Ideally I should have requested the whole file to edit it properly, but let's try to update User and Case.



from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .security import SecureFileHandler
from . import models, database, schemas, embeddings
from sqlalchemy.orm import Session
from .database import engine, get_db
from fastapi import FastAPI, UploadFile, File, Depends, Form, Request, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .audit_logger import log_action
from . import auth
from jose import JWTError, jwt

app = FastAPI(title="Bina Legal API", version="1.0.0")

# Security Dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# CORS Middleware for Frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@app.get("/")
def read_root():
    return {"status": "Bina Backend Running", "system": "Secure"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    case_id: int = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    secure_handler = SecureFileHandler()
    
    # 1. Save Encrypted File (Standard Logic)
    encrypted_path = await secure_handler.save_encrypted_file(file)
    
    # 2. OCR Processing (Hybrid)
    extracted_text_content = ""
    try:
        # Create a temp file with the original content for OCR processing
        # We need to read the file again or use the encrypted one and decrypt it.
        # Since we just read `await file.read()` in save_encrypted_file, `file` cursor is at end.
        # It's better to decrypt the saved file to a temp location.
        
        # Determine extension
        ext = os.path.splitext(file.filename)[1].lower()
        if not ext:
            ext = ".tmp"
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_ocr_file:
            # Decrypt the file we just saved to getting back original content
            decrypted_content = secure_handler.decrypt_file(encrypted_path)
            temp_ocr_file.write(decrypted_content)
            temp_ocr_path = temp_ocr_file.name
            
        # Perform OCR
        ocr_service = OCRService()
        mime_type = file.content_type or "application/octet-stream"
        
        # Fix mime type for PDF if generic
        if ext == ".pdf":
            mime_type = "application/pdf"
            
        print(f"Starting OCR for {file.filename} ({mime_type})...")
        extracted_text_content = ocr_service.extract_text(temp_ocr_path, mime_type)
        print(f"OCR Complete. Extracted {len(extracted_text_content)} chars.")
        
        # Secure cleanup of temp file
        os.remove(temp_ocr_path)
        
    except Exception as e:
        print(f"OCR Pipeline Error: {e}")
        # Non-blocking error, we still save the file
        extracted_text_content = "" # Ensure it's empty string if failed

    
    # Generate Embedding Stub
    emb_service = embeddings.EmbeddingService()
    # Use extracted text ideally, but fallback to stub for now if expense concern
    # For now, let's keep the mock text or use a snippet of OCR?
    # Let's use the first 500 chars of OCR if available for embedding context!
    embed_input = extracted_text_content[:1000] if extracted_text_content else "mock text content"
    vector = emb_service.get_embedding(embed_input)

    # Save to DB
    db_doc = models.Document(
        filename=file.filename,
        file_path=encrypted_path,
        case_id=case_id,
        embedding=vector,
        extracted_text=extracted_text_content
        # In multi-tenant, ensure document belongs to user's organization if applicable
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    log_action(db, request if 'request' in locals() else None, "UPLOAD", f"Uploaded {file.filename}. OCR chars: {len(extracted_text_content)}", user_id=current_user.id, user_type="User") 
    return {
        "filename": file.filename, 
        "status": "encrypted", 
        "path": encrypted_path,
        "document_id": db_doc.id,
        "case_id": case_id,
        "ocr_status": "success" if extracted_text_content else "no-text/failed"
    }

@app.get("/cases", response_model=List[schemas.Case])
def get_cases(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # SaaS Logic: Filter by Organization
    if current_user.role == 0: # SuperAdmin
        cases = db.query(models.Case).all()
    else:
        cases = db.query(models.Case).filter(models.Case.organization_id == current_user.organization_id).all()
        
    log_action(db, request, "CONSULT", "Viewed case list", user_id=current_user.id, user_type="User")
    return cases

@app.post("/cases", response_model=schemas.Case)
def create_case(request: Request, case: schemas.CaseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_case = models.Case(
        title=case.title, 
        description=case.description, 
        organization_id=current_user.organization_id
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    log_action(db, request, "CREATE", f"Created case {db_case.id}: {db_case.title}", user_id=current_user.id, user_type="User")
    return db_case

@app.get("/chat/{case_id}", response_model=List[schemas.Message])
def get_chat_history(case_id: int, request: Request, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(models.Message.case_id == case_id).order_by(models.Message.timestamp).all()
    log_action(db, request, "CONSULT", f"Viewed chat history for case {case_id}")
    return messages

@app.post("/chat", response_model=schemas.Message)
def chat_endpoint(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    # 1. Save user message
    user_msg = models.Message(
        sender="user",
        content=message.content,
        case_id=message.case_id
    )
    db.add(user_msg)
    db.commit()

    # 2. Generate AI Response using Global Generative Language API (Service Account)
    import httpx
    import os
    import google.auth
    from google.auth.transport.requests import Request

    # PROJECT_ID is still needed for x-goog-user-project header sometimes
    PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
    ai_response_text = "Lo siento, no puedo procesar tu solicitud en este momento."

    try:
        # Get Access Token
        credentials, project = google.auth.default(
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/generative-language"
            ]
        )
        auth_req = Request()
        credentials.refresh(auth_req)
        token = credentials.token

        # Global API Endpoint
        # Using gemini-2.0-flash as it was found in the available models list
        model_name = "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-goog-user-project": PROJECT_ID
        }
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": message.content}]
            }],
            "generationConfig": {
                "temperature": 0.5,
                "maxOutputTokens": 1024
            }
        }

        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        
        if response.status_code != 200:
            print(f"Global AI Chat Error: {response.text}")
            ai_response_text = f"Error del sistema: {response.status_code}"
        else:
            data = response.json()
            if "candidates" in data and data["candidates"]:
                candidate = data["candidates"][0]
                if "content" in candidate:
                    ai_response_text = candidate["content"]["parts"][0]["text"]
                else:
                    ai_response_text = "La IA no generó respuesta (posible bloqueo de seguridad)."
    except Exception as e:
        print(f"Error calling Global AI API: {e}")
        ai_response_text = f"Error: {str(e)}"
    
    ai_msg = models.Message(
        sender="ai",
        content=ai_response_text,
        case_id=message.case_id
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    
    return ai_msg

@app.delete("/cases/{case_id}")
def delete_case(case_id: int, request: Request, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    db.delete(case)
    db.commit()
    log_action(db, request, "DELETE", f"Deleted case {case_id}")
    return {"status": "deleted", "case_id": case_id}

@app.get("/download/{document_id}")
def download_file(document_id: int, request: Request, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Decrypt file for download
    secure_handler = SecureFileHandler()
    try:
        decrypted_content = secure_handler.decrypt_file(doc.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error decrypting file")
    
    # Save temporarily to send
    # Ideally use a tempfile module, but for simplicity:
    import os
    temp_path = f"temp_{doc.filename}"
    with open(temp_path, "wb") as f:
        f.write(decrypted_content)
        
    log_action(db, request, "DOWNLOAD", f"Downloaded document {document_id}: {doc.filename}")
    
    # Use BackgroundTasks to clean up if we were doing this properly for prod
    return FileResponse(temp_path, filename=doc.filename)

# SaaS Management Endpoints

@app.post("/organizations", dependencies=[Depends(get_current_user)])
def create_organization(name: str = Form(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != 0: # Only SuperAdmin
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org = models.Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    log_action(db, None, "CREATE_ORG", f"Created Organization {org.id}: {org.name}", user_id=current_user.id, user_type="SuperAdmin")
    return org

@app.post("/users", dependencies=[Depends(get_current_user)])
def create_user(
    email: str = Form(...), 
    password: str = Form(...), 
    role: int = Form(...), 
    organization_id: int = Form(None),
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Authorization Logic
    if current_user.role == 0: # SuperAdmin can create any user
        pass
    elif current_user.role == 1: # OrgAdmin can only create users for their org
        if role <= 1: # Cannot create SuperAdmin or other OrgAdmins (simplification)
             raise HTTPException(status_code=403, detail="Cannot create Admins")
        organization_id = current_user.organization_id # Force org_id
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    hashed_pw = auth.get_password_hash(password)
    user = models.User(email=email, hashed_password=hashed_pw, role=role, organization_id=organization_id)
    db.add(user)
    db.commit()
    return {"status": "User created", "email": email}


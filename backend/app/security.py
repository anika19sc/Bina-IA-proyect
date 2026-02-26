from cryptography.fernet import Fernet
import os
from fastapi import UploadFile

class SecureFileHandler:
    def __init__(self):
        # In production, load this from environment variables!
        self.key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        self.cipher_suite = Fernet(self.key)
        self.upload_dir = "secure_uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_encrypted_file(self, file: UploadFile) -> str:
        contents = await file.read()
        encrypted_contents = self.cipher_suite.encrypt(contents)
        
        file_path = os.path.join(self.upload_dir, f"{file.filename}.enc")
        
        with open(file_path, "wb") as f:
            f.write(encrypted_contents)
            
        return file_path

    def decrypt_file(self, file_path: str) -> bytes:
        with open(file_path, "rb") as f:
            encrypted_contents = f.read()
            
        return self.cipher_suite.decrypt(encrypted_contents)

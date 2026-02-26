from sqlalchemy.orm import Session
from . import models
from fastapi import Request

def log_action(db: Session, request: Request, action: str, details: str = None, user_id: int = None, user_type: str = "System"):
    """
    Logs an action to the audit_logs table.
    """
    client_ip = request.client.host if request.client else "Unknown"
    
    # If we had real auth, we would get the user_id from the request/token
    # For now, we default to "System" or "Local User"
    
    audit_log = models.AuditLog(
        user_id=user_id, # Nullable if generic user
        user_type=user_type, # 'System', 'Lawyer', etc.
        action=action,
        details=details,
        ip_address=client_ip
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log

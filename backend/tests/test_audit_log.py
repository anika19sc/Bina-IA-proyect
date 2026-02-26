from unittest.mock import MagicMock
from app.audit_logger import log_action
from app.models import AuditLog

def test_log_action_creates_entry():
    # Mock DB Session
    mock_db = MagicMock()
    
    # Mock Request
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"
    
    # Call function
    action = "TEST_ACTION"
    details = "Test details"
    log_entry = log_action(mock_db, mock_request, action, details)
    
    # Assertions
    assert isinstance(log_entry, AuditLog)
    assert log_entry.action == action
    assert log_entry.details == details
    assert log_entry.ip_address == "127.0.0.1"
    
    # Verify DB interactions
    mock_db.add.assert_called_once_with(log_entry)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(log_entry)

if __name__ == "__main__":
    try:
        test_log_action_creates_entry()
        print("Audit Log Test Passed!")
    except AssertionError as e:
        print(f"Audit Log Test Failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

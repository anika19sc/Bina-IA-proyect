import sys
# Force utf-8 for stdout just in case
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from sqlalchemy import create_engine, text

# Explicitly use 127.0.0.1
DATABASE_URL = "postgresql://user:password@127.0.0.1:5432/binadb"

def migrate():
    print("Starting migration (Robust)...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("Connected to database!")
            
            # Check column
            check_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='documents' AND column_name='extracted_text'")
            result = conn.execute(check_sql)
            
            if result.fetchone():
                print("Column 'extracted_text' already exists.")
            else:
                print("Adding 'extracted_text' column...")
                alter_sql = text("ALTER TABLE documents ADD COLUMN extracted_text TEXT")
                conn.execute(alter_sql)
                conn.commit()
                print("Migration successful: Column added.")
                
    except Exception as e:
        print("MIGRATION FAILED")
        try:
            # Safe print of error
            error_msg = str(e)
            print(error_msg.encode('ascii', 'replace').decode('ascii'))
        except:
            print("Unknown error (encoding failure)")

if __name__ == "__main__":
    migrate()

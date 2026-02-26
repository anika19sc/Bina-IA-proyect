DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='extracted_text') THEN 
        ALTER TABLE documents ADD COLUMN extracted_text TEXT; 
    END IF; 
END $$;

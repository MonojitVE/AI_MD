from sqlalchemy import text
from app.database import SyncSessionLocal

def run_migration():
    session = SyncSessionLocal()
    try:
        # Alter alerts table
        session.execute(text('''
            ALTER TABLE alerts 
            ADD COLUMN IF NOT EXISTS assigned_to VARCHAR,
            ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending',
            ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium',
            ADD COLUMN IF NOT EXISTS accepted_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS started_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP;
        '''))
        
        # Add foreign key separately in case it fails if it exists
        try:
            session.execute(text('''
                ALTER TABLE alerts 
                ADD CONSTRAINT fk_alerts_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(id);
            '''))
        except Exception as e:
            print(f"FK constraint might already exist or failed: {e}")
            session.rollback()

        # Alter maintenance_logs table
        session.execute(text('''
            ALTER TABLE maintenance_logs 
            ADD COLUMN IF NOT EXISTS resolution TEXT,
            ADD COLUMN IF NOT EXISTS repair_duration_minutes INTEGER,
            ADD COLUMN IF NOT EXISTS follow_up_required BOOLEAN DEFAULT FALSE;
        '''))
        
        session.commit()
        print("Migration completed successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error during migration: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()

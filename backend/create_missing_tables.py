from app.database import sync_engine, Base
from app.models.user import User
from app.models.alert import Alert, MaintenanceLog
from app.models.equipment import Equipment, SensorReading
from app.models.inventory import InventoryItem, Supplier
from app.models.defect import DefectRecord

def create_tables():
    Base.metadata.create_all(sync_engine)
    print("Created missing tables.")

if __name__ == "__main__":
    create_tables()

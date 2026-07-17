from app.database.session import engine, Base
from app.models.backup_job import BackupJob
from app.models.users import User
from app.models.report import Report


Base.metadata.create_all(bind=engine)

print("Tables created successfully!")

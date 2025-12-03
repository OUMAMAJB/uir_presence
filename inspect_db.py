from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tables:", tables)
    
    if 'subjects' in tables:
        columns = [c['name'] for c in inspector.get_columns('subjects')]
        print("Subjects columns:", columns)

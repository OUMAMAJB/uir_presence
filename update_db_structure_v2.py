from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        try:
            # 1. Add track_id column
            print("Checking track_id column...")
            result = conn.execute(text("SHOW COLUMNS FROM academic_years LIKE 'track_id'"))
            if result.rowcount == 0:
                print("Adding track_id column to academic_years table...")
                conn.execute(text("ALTER TABLE academic_years ADD COLUMN track_id INTEGER REFERENCES tracks(id)"))
                print("Column track_id added successfully.")
            else:
                print("Column track_id already exists.")
            
            # 2. Drop unique constraint on name
            print("Checking unique constraint on name...")
            # This is tricky in MySQL as we need the constraint name.
            # Usually it's 'name' or 'name_2' or similar.
            # We can try to drop index 'name' if it exists.
            try:
                conn.execute(text("DROP INDEX name ON academic_years"))
                print("Unique index 'name' dropped.")
            except Exception as e:
                print(f"Could not drop index 'name' (might not exist or different name): {e}")
                
        except Exception as e:
            print(f"Error updating database: {e}")

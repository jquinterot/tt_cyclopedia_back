from app.config.postgres_config import engine, Base
from sqlalchemy import text

def create_schema_if_not_exists(engine, schema_name):
    try:
        # Directly execute SQL to create the schema (avoids reflection issues)
        with engine.begin() as connection:  # Auto-commits on success
            connection.execute(
                text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            )
        print(f"Schema '{schema_name}' created or confirmed to exist.")
    except Exception as e:
        print(f"Error creating schema: {e}")

if __name__ == "__main__":
    create_schema_if_not_exists(engine, "cyclopedia_owner")
    Base.metadata.create_all(bind=engine)  # Create tables in the schema
    print("Database initialized.")
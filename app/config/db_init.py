from app.config.postgres_config import engine, Base  # Import engine and Base
from sqlalchemy import MetaData, DDL


def create_schema_if_not_exists(engine, schema_name):
    try:
        # Reflect the database metadata
        metadata = MetaData()
        metadata.reflect(bind=engine)

        if schema_name not in metadata.schemas:
            DDL(f"CREATE SCHEMA IF NOT EXISTS {schema_name}").execute(engine)
            print(f"Schema '{schema_name}' created (or already existed).")
        else:
            print(f"Schema '{schema_name}' already exists.")

    except Exception as e:
        print(f"Error creating schema: {e}")


if __name__ == "__main__":
    create_schema_if_not_exists(engine, "cyclopedia_owner")
    Base.metadata.create_all(bind=engine)  # Create tables in the schema
    print("Database initialized.")

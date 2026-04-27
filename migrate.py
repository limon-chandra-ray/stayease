import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

schema_path = os.path.join(os.path.dirname(__file__), "agent", "schema.sql")

with open(schema_path, "r") as f:
    sql = f.read()

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()

print("Migration applied successfully!")

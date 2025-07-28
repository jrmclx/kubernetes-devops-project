from sqlalchemy import create_engine, MetaData
import os

import logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Database connection setup
# DATABASE_URL environment variable must be set (ex: Docker/K8s env)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)

meta = MetaData()

try:
    conn = engine.connect()
except Exception as e:
    logging.error(f"Database connection failed: {e}")
    raise
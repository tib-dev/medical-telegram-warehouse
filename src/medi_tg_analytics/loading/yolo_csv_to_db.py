import os
import sys
import logging
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from medi_tg_analytics.core.settings import settings

# ------------------------------------------------------------------
# Setup & Paths
# ------------------------------------------------------------------
load_dotenv()

# Ensure this matches your actual filename from Task 3
YOLO_CSV_PATH: Path = settings.paths.DATA["raw_dir"] / \
    "yolo_image_detections.csv"
FLAG_FILE: Path = settings.paths.DATA["interim_dir"] / "yolo_loaded.flag"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def get_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
    except psycopg2.Error as e:
        logging.error(f" Database connection failed: {e}")
        sys.exit(1)


# ------------------------------------------------------------------
# SQL Definitions
# ------------------------------------------------------------------
# Explicitly matching your 5 CSV fields
CREATE_TABLE_SQL = """
CREATE TABLE raw.yolo_image_detections (
    message_id       BIGINT,
    channel_name     TEXT,
    detected_class   TEXT,
    confidence_score NUMERIC(5,4),
    image_category   TEXT,
    ingested_at      TIMESTAMP DEFAULT now()
);
"""


def load_yolo_csv_to_raw():
    if not YOLO_CSV_PATH.exists():
        logging.error(f"YOLO CSV not found: {YOLO_CSV_PATH}")
        sys.exit(1)

    conn = get_connection()
    cur = conn.cursor()

    try:
        logging.info("Dropping old table to refresh schema...")
        # CASCADE ensures any dependent views are also handled
        cur.execute("DROP TABLE IF EXISTS raw.yolo_image_detections CASCADE;")

        logging.info("Creating fresh table with 5 columns...")
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()

        logging.info(f"Streaming data from {YOLO_CSV_PATH.name}...")

        with open(YOLO_CSV_PATH, 'r', encoding='utf-8') as f:
            # COPY is the fastest method for CSV loading in Postgres
            copy_sql = """
                COPY raw.yolo_image_detections(
                    message_id, 
                    channel_name, 
                    detected_class, 
                    confidence_score, 
                    image_category
                )
                FROM STDIN WITH (FORMAT CSV, HEADER TRUE);
            """
            cur.copy_expert(copy_sql, f)

        conn.commit()
        logging.info(f"Successfully loaded all detections.")

        # Create flag for Dagster/DVC
        FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(FLAG_FILE, "w") as f:
            f.write("yolo_loaded")

    except Exception as e:
        conn.rollback()
        logging.error(f"Critical error during load: {e}")
        sys.exit(1)  # Crucial for Dagster to catch the failure
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load_yolo_csv_to_raw()

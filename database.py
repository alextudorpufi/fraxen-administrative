# database.py
import os
import psycopg2
from collections import namedtuple
from dotenv import load_dotenv

load_dotenv()

# Define structures here so both files can access them
Executive = namedtuple('Executive', ['id', 'experience', 'gender', 'location', 'sector_focus', 'title'])
Highlight = namedtuple('Highlight', ['id', 'company_descri', 'details', 'display_order', 'position_title', 'executive_id'])
Strength = namedtuple('Strength', ['id', 'display_order', 'strength_descrip', 'executive_id'])

def get_db_connection():
    """Establishes and returns a database connection."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT")
    )

def fetch_all_data():
    """Fetches and structures all data from the database."""
    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        # 1. Fetch Executives
        cursor.execute("SELECT * FROM executives ORDER BY id")
        exec_records = [
            Executive(r[0], r[1], r[2], r[3], [s.strip() for s in r[4].split(',')], [t.strip() for t in r[5].split('|')])
            for r in cursor.fetchall()
        ]

        # 2. Fetch Highlights
        cursor.execute("SELECT * FROM executive_highlights ORDER BY executive_id, display_order")
        highlights = [Highlight(*row) for row in cursor.fetchall()]

        # 3. Fetch Strengths
        cursor.execute("SELECT * FROM executive_strengths ORDER BY executive_id, display_order")
        strengths = [Strength(*row) for row in cursor.fetchall()]

        return exec_records, highlights, strengths
    finally:
        connection.close()
import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

# 1. This line loads the variables from your .env file into the system
load_dotenv()

def test_connection():
    connection = None
    try:
        print("Connecting to the PostgreSQL database...")
        
        # 2. Pull the values from the environment instead of hardcoding them
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT")
        )

        cursor = connection.cursor()
        
        # 3. Simple query to verify it works
        query = "select * from executive_strengths where executive_id = 1;"
        cursor.execute(query)

        records = cursor.fetchall()
        
        print(f"\nSuccessfully connected! Total rows fetched: {len(records)}")
        print("-" * 30)
        for row in records:
            print(row)
        print("-" * 30)

    except (Exception, Error) as error:
        print(f"Error while connecting to PostgreSQL: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed.")

if __name__ == "__main__":
    test_connection()
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_postgres():
    print("Waiting for PostgreSQL to be ready...")
    while True:
        try:
            connection = psycopg2.connect(
                dbname="STORAgeDB", 
                user="EmmaDB",
                password="1234STORAge!",
                host="postgres"
            )
            connection.close()
            print("PostgreSQL is ready.")
            break
        except OperationalError:
            print("PostgreSQL is not ready yet, waiting...")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_postgres()


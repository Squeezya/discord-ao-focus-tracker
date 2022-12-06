import os
from dotenv import load_dotenv
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager

load_dotenv()

dbConnection = f"dbname='{os.environ['POSTGRES_DB']}' " \
               f"user='{os.environ['POSTGRES_USER']}' " \
               f"host='{os.environ['POSTGRES_HOST']}' " \
               f"password='{os.environ['POSTGRES_PASSWORD']}'"
connection_pool = ThreadedConnectionPool(1, 10, dsn=dbConnection)



@contextmanager
def get_cursor():
    con = connection_pool.getconn()
    try:
        yield con.cursor()
        con.commit()
    finally:
        connection_pool.putconn(con)

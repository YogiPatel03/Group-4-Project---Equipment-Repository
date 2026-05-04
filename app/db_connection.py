import mysql.connector
import os

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database="school_inventory"
    )
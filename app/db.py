"""Conexión compartida a PostgreSQL y comprobación local del entorno."""

import os

import psycopg


def connect():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )


if __name__ == "__main__":
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone() == (1,)
    print("PostgreSQL: conexión correcta")

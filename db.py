
import os
import json
import oracledb
from dotenv import load_dotenv

load_dotenv(".env")


def get_connection():
    dsn = (
        "(description="
        "(address=(protocol=tcps)"
        f"(host={os.getenv('DB_HOST')})"
        f"(port={os.getenv('DB_PORT')})"
        ")"
        "(connect_data="
        f"(service_name={os.getenv('DB_SERVICE')})"
        ")"
        ")"
    )

    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=dsn
    )


def get_items():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ITEM_ID, ITEM_NAME, PRICE, ITEM_VALUE
                FROM ITEMS
                ORDER BY ITEM_ID
            """)

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "price": int(row[2]),
                    "value": int(row[3])
                }
                for row in cursor.fetchall()
            ]
    finally:
        connection.close()


def save_selection(budget, total_cost, total_value, selected_items):
    connection = get_connection()

    try:
        selected_names = [
            item["name"] for item in selected_items
        ]

        with connection.cursor() as cursor:
            cursor.callproc(
                "SAVE_SELECTION",
                [
                    budget,
                    total_cost,
                    total_value,
                    json.dumps(selected_names)
                ]
            )

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

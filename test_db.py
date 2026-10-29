
from db import get_connection, get_items

try:
    connection = get_connection()
    print("Oracle connection successful!")
    connection.close()

    print("Items from Oracle:")
    for item in get_items():
        print(item)

except Exception as error:
    print("Connection error:", error)

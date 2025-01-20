import pymysql

# Connect to the MySQL server (replace 'localhost', 'your_password', etc. with your settings)
connection = pymysql.connect(
    host="localhost", user="root", password="your_password", database="mysql"
)

try:
    with connection.cursor() as cursor:
        # Create a new database
        cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
        print("Database created!")

        # Switch to the new database
        cursor.execute("USE test_db")

        # Create a new table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100)
            )
        """
        )
        print("Table created!")

    connection.commit()
finally:
    connection.close()

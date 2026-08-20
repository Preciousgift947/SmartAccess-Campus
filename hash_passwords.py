import bcrypt
import mysql.connector
from config import Config


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


conn = mysql.connector.connect(
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB,
    port=Config.MYSQL_PORT
)

cursor = conn.cursor()

tables = ["STUDENT", "LECTURER", "ADMIN"]

for table in tables:

    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()

    columns = [column[0] for column in cursor.description]

    password_index = columns.index("Password_Hash")

    id_column = {
        "STUDENT": "Student_ID",
        "LECTURER": "Lecturer_ID",
        "ADMIN": "Admin_ID"
    }[table]

    id_index = columns.index(id_column)

    for row in rows:

        user_id = row[id_index]
        current_password = row[password_index]

        # Do not hash an already-hashed password
        if current_password and current_password.startswith("$2"):
            continue

        hashed_password = hash_password(current_password)

        cursor.execute(
            f"""
            UPDATE {table}
            SET Password_Hash = %s
            WHERE {id_column} = %s
            """,
            (hashed_password, user_id)
        )

    print(f"{table}: passwords processed")

conn.commit()

cursor.close()
conn.close()

print("All passwords have been securely processed.")
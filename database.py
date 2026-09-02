import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST", os.getenv("DB_HOST")),
        port=int(os.getenv("MYSQLPORT", os.getenv("DB_PORT", "3306"))),
        user=os.getenv("MYSQLUSER", os.getenv("DB_USER")),
        password=os.getenv("MYSQLPASSWORD", os.getenv("DB_PASSWORD")),
        database=os.getenv("MYSQLDATABASE", os.getenv("DB_NAME"))
    )


def init_database():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booster_roles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                guild_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                role_id VARCHAR(255) NOT NULL,
                role_name VARCHAR(255) NOT NULL,
                color_1 VARCHAR(255),
                color_2 VARCHAR(255),

                UNIQUE KEY unique_user_guild (guild_id, user_id),
                UNIQUE KEY unique_role (role_id)
            )
        """)

        connection.commit()

        print("✅ Database booster_roles siap.")

    except Error as error:
        print(f"❌ Database Error: {error}")

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def get_booster_role(guild_id, user_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM booster_roles
            WHERE guild_id = %s
              AND user_id = %s
        """, (
            str(guild_id),
            str(user_id)
        ))

        return cursor.fetchone()

    except Error as error:
        print(f"❌ Get Booster Role Error: {error}")
        return None

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def save_booster_role(
    guild_id,
    user_id,
    role_id,
    role_name=None,
    color_1=None,
    color_2=None
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO booster_roles
            (
                guild_id,
                user_id,
                role_id,
                role_name,
                color_1,
                color_2
            )
            VALUES (%s, %s, %s, %s, %s, %s)

            ON DUPLICATE KEY UPDATE
                role_id = VALUES(role_id),
                role_name = VALUES(role_name),
                color_1 = VALUES(color_1),
                color_2 = VALUES(color_2)
        """, (
            str(guild_id),
            str(user_id),
            str(role_id),
            role_name or "",
            color_1,
            color_2
        ))

        connection.commit()

        return True

    except Error as error:
        print(f"❌ Save Booster Role Error: {error}")
        return False

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def delete_booster_role(
    guild_id,
    user_id
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM booster_roles
            WHERE guild_id = %s
              AND user_id = %s
        """, (
            str(guild_id),
            str(user_id)
        ))

        connection.commit()

        return True

    except Error as error:
        print(f"❌ Delete Booster Role Error: {error}")
        return False

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

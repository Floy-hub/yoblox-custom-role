import mysql.connector

from config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
)


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booster_roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            role_id BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE KEY unique_user_role (guild_id, user_id),
            UNIQUE KEY unique_role (guild_id, role_id)
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


def get_booster_role(guild_id: int, user_id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM booster_roles
        WHERE guild_id = %s AND user_id = %s
        LIMIT 1
    """, (guild_id, user_id))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result


def save_booster_role(guild_id: int, user_id: int, role_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO booster_roles
            (guild_id, user_id, role_id)
        VALUES
            (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            role_id = VALUES(role_id)
    """, (guild_id, user_id, role_id))

    connection.commit()

    cursor.close()
    connection.close()


def delete_booster_role(guild_id: int, user_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM booster_roles
        WHERE guild_id = %s AND user_id = %s
    """, (guild_id, user_id))

    connection.commit()

    cursor.close()
    connection.close()
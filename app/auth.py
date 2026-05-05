from .db_connection import get_connection

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT user_id, first_name, last_name, email, password_hash, role, status
        FROM Users
        WHERE email = %s
    """, (email,))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:
        return None

    if user["status"] != "active":
        return None

    # Temporary check for now
    if user["password_hash"] == password:
        return user

    return None
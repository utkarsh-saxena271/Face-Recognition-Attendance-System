from app.models.db import get_db_connection, get_user_by_username, verify_password
import getpass

def clear_all_users_except_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE role != 'admin'")
        user_ids = [row[0] for row in cursor.fetchall()]

        if not user_ids:
            print("ℹ️ No non-admin users found")
            return

        cursor.executemany(
            "DELETE FROM attendance WHERE user_id = ?", 
            [(uid,) for uid in user_ids]
        )

        cursor.executemany(
            "DELETE FROM email_notifications WHERE user_id = ?", 
            [(uid,) for uid in user_ids]
        )

        cursor.execute("DELETE FROM users WHERE role != 'admin'")

        conn.commit()
        print("✅ All users (except admin) deleted successfully")

    except Exception as e:
        print("❌ Error:", str(e))

    finally:
        conn.close()


if __name__ == "__main__":
    print("🔐 ADMIN AUTH REQUIRED")

    username = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")

    admin = get_user_by_username(username)

    if not admin or admin.get("role") != "admin":
        print("❌ Not an admin user")
        exit()

    if not verify_password(admin["password_hash"], password):
        print("❌ Incorrect password")
        exit()

    confirm = input("⚠️ This will DELETE ALL USERS except ADMIN. Type 'YES' to continue: ")

    if confirm.strip().lower() == "yes":
        clear_all_users_except_admin()
    else:
        print("❌ Operation cancelled")
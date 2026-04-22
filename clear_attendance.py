from app.models.db import get_db_connection, get_user_by_username, verify_password
import getpass

def clear_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM attendance")
        conn.commit()
        print("✅ All attendance deleted successfully")

    except Exception as e:
        print("❌ Error:", str(e))

    finally:
        conn.close()


if __name__ == "__main__":
    print("🔐 ADMIN AUTH REQUIRED")

    username = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")

    admin = get_user_by_username(username)

    # Check if user exists and is admin
    if not admin or admin.get("role") != "admin":
        print("❌ Not an admin user")
        exit()

    # Verify password
    if not verify_password(admin["password_hash"], password):
        print("❌ Incorrect password")
        exit()

    # Final confirmation
    confirm = input("⚠️ This will DELETE ALL ATTENDANCE. Type 'YES' to continue: ")

    if confirm.strip().lower() == "yes":
        clear_attendance()
    else:
        print("❌ Operation cancelled")
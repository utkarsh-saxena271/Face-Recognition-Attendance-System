# email_service.py

class EmailService:
    """
    Email disabled - handled by EmailJS (frontend)
    """

    def send_email(self, *args, **kwargs):
        print("⚠️ Email skipped (EmailJS is handling emails)")
        return True

    def send_attendance_marked_email(self, *args, **kwargs):
        print("⚠️ Attendance email skipped (EmailJS)")
        return True

    def send_absent_notification(self, *args, **kwargs):
        print("⚠️ Absent email skipped (EmailJS)")
        return True

    def send_daily_summary(self, *args, **kwargs):
        print("⚠️ Summary email skipped (EmailJS)")
        return True


# global instance
email_service = EmailService()
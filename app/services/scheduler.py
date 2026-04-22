from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime, timezone, timedelta
from app.models.db import (
    get_all_users, check_and_mark_absent, generate_daily_report,
    get_user_monthly_summary, get_attendance_today, log_audit
)
from app.services.email_service import email_service

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(daemon=True)

class AttendanceScheduler:
    """Scheduler for automated attendance tasks"""
    
    @staticmethod
    def mark_end_of_day_absentees():
        """Mark users as absent if not marked by end of day (5 PM)"""
        try:
            logger.info('🔄 Starting end-of-day absent marking...')
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            
            all_users = get_all_users()
            marked_count = 0
            
            for user in all_users:
                if user.get('embedding'):  # Only face-registered users
                    if check_and_mark_absent(user['id'], today):
                        marked_count += 1
                        logger.info(f"✓ Marked {user['username']} as absent")
                        
                        # Log audit
                        log_audit(
                            user['id'],
                            'auto_absent_marked',
                            'attendance',
                            None,
                            f'Automatically marked absent for {today}'
                        )
            
            logger.info(f'✅ End-of-day marking complete. {marked_count} users marked absent.')
            
        except Exception as e:
            logger.error(f'❌ Error in mark_end_of_day_absentees: {str(e)}')
    
    @staticmethod
    def send_daily_summaries():
        """Send daily attendance summaries to all users"""
        try:
            logger.info('📧 Sending daily attendance summaries...')
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            
            today_records = get_attendance_today()
            sent_count = 0
            
            for record in today_records:
                if record.get('email'):
                    summary_data = {
                        'date': today,
                        'present': 1 if record['status'] == 'present' else 0,
                        'late': 1 if record['status'] == 'late' else 0,
                        'absent': 1 if record['status'] == 'absent' else 0,
                        'time': record.get('time_in', 'N/A')
                    }
                    
                    if email_service.send_daily_summary(
                        record['user_id'],
                        record['email'],
                        record['full_name'],
                        summary_data
                    ):
                        sent_count += 1
                        logger.info(f"✓ Daily summary sent to {record['email']}")
            
            logger.info(f'✅ Daily summaries complete. {sent_count} emails sent.')
            
        except Exception as e:
            logger.error(f'❌ Error in send_daily_summaries: {str(e)}')
    
    @staticmethod
    def generate_monthly_reports():
        """Generate monthly attendance reports"""
        try:
            logger.info('📊 Generating monthly reports...')
            today = datetime.now(timezone.utc)
            year = today.year
            month = today.month
            
            all_users = get_all_users()
            report_count = 0
            
            for user in all_users:
                report = get_user_monthly_summary(user['id'], year, month)
                if report:
                    report_count += 1
                    logger.info(f"✓ Generated monthly report for {user['username']}")
                    
                    # Log audit
                    log_audit(
                        user['id'],
                        'monthly_report_generated',
                        'attendance_report',
                        None,
                        f'Monthly summary: {report["present"]} present, {report["absent"]} absent, {report["late"]} late'
                    )
            
            logger.info(f'✅ Monthly reports generated. {report_count} reports created.')
            
        except Exception as e:
            logger.error(f'❌ Error in generate_monthly_reports: {str(e)}')


def start_scheduler():
    """Start the background scheduler"""
    try:
        # Schedule: Mark absentees every day at 5:30 PM UTC (17:30:00)
        scheduler.add_job(
            AttendanceScheduler.mark_end_of_day_absentees,
            CronTrigger(hour=17, minute=30, day_of_week='0-4'),  # Mon-Fri
            id='mark_absentees',
            name='Mark End-of-Day Absentees',
            replace_existing=True
        )
        logger.info('✓ Scheduled: Mark absentees (5:30 PM UTC, Mon-Fri)')
        
        # Schedule: Send daily summaries at 6:00 PM UTC (18:00:00)
        scheduler.add_job(
            AttendanceScheduler.send_daily_summaries,
            CronTrigger(hour=18, minute=0),
            id='send_summaries',
            name='Send Daily Summaries',
            replace_existing=True
        )
        logger.info('✓ Scheduled: Send daily summaries (6:00 PM UTC, daily)')
        
        # Schedule: Generate monthly reports on 1st of each month at 11:00 PM UTC
        scheduler.add_job(
            AttendanceScheduler.generate_monthly_reports,
            CronTrigger(day=1, hour=23, minute=0),
            id='monthly_reports',
            name='Generate Monthly Reports',
            replace_existing=True
        )
        logger.info('✓ Scheduled: Generate monthly reports (1st of month at 11 PM UTC)')
        
        if not scheduler.running:
            scheduler.start()
            logger.info('✅ Attendance scheduler started successfully')
        
        return True
        
    except Exception as e:
        logger.error(f'❌ Error starting scheduler: {str(e)}')
        return False


def stop_scheduler():
    """Stop the background scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info('✅ Scheduler stopped')
        return True
    except Exception as e:
        logger.error(f'❌ Error stopping scheduler: {str(e)}')
        return False


def get_scheduled_jobs():
    """Get all scheduled jobs"""
    return scheduler.get_jobs()


def pause_scheduler():
    """Pause the scheduler"""
    scheduler.pause()
    logger.info('⏸ Scheduler paused')


def resume_scheduler():
    """Resume the scheduler"""
    scheduler.resume()
    logger.info('▶ Scheduler resumed')

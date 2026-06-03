from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from core.logger import logger
from core.database import get_upcoming_reminders, mark_reminder_sent
from config import Config

# Create scheduler instance
# AsyncIOScheduler works with our async telegram bot
scheduler = AsyncIOScheduler()

async  def check_and_send_reminders(bot):
    """
    Runs every 30 minutes automatically.
    Checks if any appointments are coming up in 1 hour.
    If yes, sends reminder to patient.
    """
    logger.info("Checking for upcoming reminders...")
    appointments = get_upcoming_reminders()

    for appointment in appointments:
        try:
            # Combine date and time slot into one datetime object
            # appointment['date'] = "2026-06-01"
            # appointment['time_slot'] = "09:00 AM"
            appointment_datetime_str = f"{appointment['date']} {appointment['time_slot']}"
            appointment_time = datetime.strptime(
                                appointment_datetime_str, "%Y-%m-%d %I:%M %p")
            
            # Calculate how many hours until appointment 
            now = datetime.now()
            time_until = appointment_time - now
            hours_until = time_until.total_seconds() / 3600

            # Send reminder if appointment is within next year 1 hour and more than 0 hours away (hasn't passed yet)
            if 0 < hours_until <= Config.REMINDER_HOURS_BEFORE:
                await send_reminder(bot, appointment)
                mark_reminder_sent(appointment['id'])
        except Exception as e:
            logger.error(f"Reminder check failed for appointment {appointment['id']}")

async def send_reminder(bot, appointment):
    """Sends reminder messsage to patient"""
    try:
        message = (
            f"⏰ *Appointment Reminder!*\n\n"
            f"Hello *{appointment['name']}!\n\n*"
            f"You have an appointment at *{Config.COMPANY_NAME}* in 1 hour.\n\n"
            f"📋 Service: {appointment['service']}\n"
            f"📅 Date: {appointment['date']}\n"
            f"🕐 Time: {appointment['time_slot']}\n\n"
            f"Please arrive 10 minutes early. See you soon! 🏥"
        )

        await bot.send_message(
            chat_id=appointment['telegram_id'],
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Reminder sent to {appointment['name']} for {appointment['date']} {appointment['time_Slot']}")

    except Exception as e:
        logger.error(f"Failed to send reminder to {appointment['telegram_id']:  {e}}")    

def start_scheduler(bot):
    """
    Starts the scheduler when bot starts.
    Runs check_and_send_reminders every 30 minutes
    """
    scheduler.add_job(
        check_and_send_reminders,
        trigger='interval',      # run repeatedly
        minutes=30,              # every 30 minutes
        args=[bot],              # pass bot so we can send messages
        id="reminder_job",  
        replace_existing=True
        )
    scheduler.start()
    logger.info("Scheduler started - checking reminders every 30 minutes")
    
    
            


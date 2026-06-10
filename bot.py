from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from core.logger import logger
from core.database import init_db
from core.scheduler import start_scheduler
from config import Config
import handlers.user as user
import handlers.admin as admin

def main():
    # Initialize database
    init_db()

    # Build application
    app = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    # ── User handlers ──────────────────────────────────────
    app.add_handler(CommandHandler("start", user.start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        user.handle_message
    ))

    # ── Button handlers ────────────────────────────────────
    # Each pattern routes to correct handler
    app.add_handler(CallbackQueryHandler(
        admin.admin_button_handler, pattern="^admin_"
    ))
    app.add_handler(CallbackQueryHandler(
        user.button_handler, pattern="^(action_|service_|date_|time_|slot_|cancel_|back_)"
    ))

    # ── Admin handlers ─────────────────────────────────────
    app.add_handler(CommandHandler("admin", admin.admin))
    app.add_handler(CommandHandler("cancelappointment", admin.cancel_appointment_admin))

    # ── Error handler ──────────────────────────────────────
    async def error_handler(update, context):
        logger.error(f"Error: {context.error}")
    app.add_error_handler(error_handler)

    # ── Start scheduler for reminders ─────────────────────
    # Pass bot instance so scheduler can send messages
    app.job_queue.run_repeating(
        callback=lambda context: __import__('asyncio').ensure_future(
            __import__('core.scheduler', fromlist=['check_and_send_reminders'])
            .check_and_send_reminders(context.bot)
        ),
        interval=1800,  # every 30 minutes
        first=10        # first run after 10 seconds
    )

    logger.info(f"{Config.AGENT_NAME} is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
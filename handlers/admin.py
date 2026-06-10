from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.database import (
    get_all_appointments,
    get_stats,
    cancel_appointment
)
from config import Config
from core.logger import logger

def is_admin(update: Update) -> bool:
    return update.effective_user.id == Config.ADMIN_ID

# ── /admin command ────────────────────────────────────────
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text('⛔ Access denied')
        return
    
    stats = get_stats()
    keyboard = []

    keyboard.append([InlineKeyboardButton("📋 View Appointments", callback_data='admin_appointments')])
    keyboard.append([InlineKeyboardButton("📅 Today's Schedule", callback_data="admin_today")])
    keyboard.append([InlineKeyboardButton("❌ Cancel Appointment", callback_data='admin_cancel')])
    
    await update.message.reply_text(
        f"📊 *Admin Panel - {Config.COMPANY_NAME}*\n\n"
        f"📋 Total Appointments: {stats['total']}\n"
        f"✅ Confirmed: {stats['confirmed']}\n"
        f"❌ Cancelled: {stats['cancelled']}\n"
        f"👥 Total Patients: {stats['total_patients']}\n",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ── Admin button handler ──────────────────────────────────
async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(update):
        await query.edit_message_text('⛔ Access denied.')
        
    if query.data == 'admin_appointments':
        await show_all_appointments(query)
    elif query.data == 'admin_today':
        await show_today_appointments(query)
    elif query.data == 'admin_cancel':
        await query.edit_message_text(
            "To cancel an appointment use:\n\n"
            "`/cancelappointment [booking_id]`\n\n"
            "Get booking ID from `/admin` → View Appointments",
            parse_mode='Markdown'
        )

# ── Show all appointments ─────────────────────────────────
async def show_all_appointments(query):
    appointments = get_all_appointments()
    if not appointments:
        await query.edit_message_text('No appointment yet.')
        return
    
    msg = "📋 *All Appointments*\n\n"
    for appointment in appointments[:10]:
        status_icon = "✅" if appointment['status'] == 'confirmed' else "❌"
        msg += (
            f"{status_icon} *{appointment['name']}*\n"
            f"  🏥 {appointment['service']}\n"
            f"  📅{appointment['date']} at {appointment['time_slot']}\n"
            f"  📱 {appointment['phone']}\n"
            f"  🆔 ID: `{appointment['id']}`\n\n"
        )
    await query.edit_message_text(msg, parse_mode='Markdown')

# ── Show today's appointments ─────────────────────────────
async def show_today_appointments(query):
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    all_appointments = get_all_appointments()

    # Filter only today's appointments from all appointments
    today_appointments = [
        appointment for appointment in all_appointments if appointment['date'] == today and appointment['status'] == 'confirmed'
    ]

    if not today_appointments:
        await query.edit_message_text(
            f"No appointments scheduled for today ({today})."
        )
        return
    
    msg = f"📅 *Today's Schedule - {today}*\n\n"
    for appointment in today_appointments:
        msg += (
            f"🕐 *{appointment['time_slot']}*\n"
            f"  👤 {appointment['name']}\n"
            f"  🏥 {appointment['service']}\n"
            f"  📱 {appointment['phone']}\n"
        )

    await query.edit_message_text(msg, parse_mode='Markdown')

# ── /cancelappointment command ────────────────────────────  
async def cancel_appointment_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /cancelappointment 5
    Admin can cancel appointment by User ID
    """
    if not is_admin(update):
        await update.message_reply_text("⛔ Access denied.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: `/cancelappointment [booking_id]`\n\n"
            "Get booking ID from View Appointments.",
            parse_mode='Markdown'
        )
        return
    
    appointment_id = int(context.args[0])

    # Admin can cancel any appointment, we pass 0 argument as telegram_id and will handle it in database
    from core.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE appointments SET status = "cancelled" WHERE id = ?',
            (appointment_id,))
        conn.commit()
        success = cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Admin cancel failed: {e}")
        success = False
    finally:
        conn.close()

    if success:
        await update.message.reply_text(
            f"✅ Appointment `{appointment_id}` cancelled successfully.",
            parse_mode='Markdown'
        )
        logger.info(f"Admin cancelled appointment {appointment_id}")
    else:
        await update.message.reply_text(
            f"❌ Appointment `{appointment_id}` not found.",
            parse_mode='Markdown'
        )




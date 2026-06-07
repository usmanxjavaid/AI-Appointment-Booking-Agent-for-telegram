from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.logger import logger
from core.database import (
    save_patient,
    save_appointment,
    is_slot_available,
    get_user_appointment,
    cancel_appointment
)
from core.validator import validate_name, validate_phone, get_available_dates
from config import Config

# ── Conversation States ───────────────────────────────────
SELECTING_ACTION = "selecting_action"
SELECTING_SERVICE = "selecting_service"
SELECTING_DATE = "selecting_date"
SELECTING_TIME = "selectig_time"
WAITING_NAME = "waiting_name"
WAITING_PHONE = "waiting_phone"
DONE = "done"

def get_user_data(context) -> dict:
    """Returns current user's booking data"""
    if 'booking' not in context.user_data:
        context.user_data['booking'] = {
            'state': SELECTING_ACTION,
            'service': None,
            'date': None,
            'date_display': None,
            'time_slot': None,
            'name': None,
            'phone': None
        }
    return context.user_data['booking']

def main_menu_keyboard() -> InlineKeyboardMarkup:
    "Builds main menu buttons for a user"
    keyboard = [
        [InlineKeyboardButton("📅 Book Appointment", callback_data='action_book')],
        [InlineKeyboardButton("📋 My Appointments", callback_data='action_view')],
        [InlineKeyboardButton("❌ Cancel Appointment", callback_data='action_cancel')]
    ]
    return InlineKeyboardMarkup(keyboard)

def service_keyboard() -> InlineKeyboardMarkup:
    "Service selection buttons from Config"
    keyboard = []
    for i, service in enumerate(Config.SERVICES):
        keyboard.append([InlineKeyboardButton(service, callback_data=f"service_{i}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back_main')])
    return InlineKeyboardMarkup(keyboard)

def date_keyboard() -> InlineKeyboardMarkup:
    """Date selection buttons for next 3 days"""
    dates = get_available_dates()
    keyboard = []
    for date in dates:
        keyboard.append([InlineKeyboardButton(date['dsiplay'], callback_data=f"date_{date['value']}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back_service')])
    return InlineKeyboardMarkup(keyboard)

def time_keyboard(date: str) -> InlineKeyboardMarkup:
    """
    Time slot buttons.
    Shows only available slots - hides already booked ones.
    """
    keyboard = []
    for i, slot in enumerate(Config.TIME_SLOTS):
        if is_slot_available(date, slot):
            keyboard.append([
                InlineKeyboardButton(f'🟢 {slot}', callback_data=f'time_{i}')
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(f"🔴 {slot} (Booked)", callback_data='slot_taken')
            ])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_date")])
    return InlineKeyboardMarkup(keyboard)

# ── /start handler ────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Booking data will get reset every time user types /start
    context.user_data['booking'] = {
        'state': SELECTING_ACTION,
        'service': None,
        'date': None,
        'date_display': None,
        'time_slot': None,
        'name': None,
        'phone': None,
    }
    logger.info(f"User Started: {user.id} - {user.first_name}")

    await update.message.reply_text(
        f"👋 Welcome to *{Config.COMPANY_NAME}*!\n\n"
        f"I'm *{Config.AGENT_NAME}*, your appointment assistant.\n\n"
        "How can i help you today?",
        reply_markup=main_menu_keyboard(),
        parse_mode='Markdown'
    )

# ── Button handler ────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    booking = get_user_data(context)
    data = query.data

    # ── Main menu actions ─────────────────────────────────
    if data == 'action_book':
        booking['state'] = SELECTING_SERVICE
        await query.edit_message_text(
            'Great! Please a service:',
            reply_markup = service_keyboard()
        )
    elif data == 'action_view':
        await show_appointments(query, user_id)
    elif data == 'action_view':
        await show_cancel_options(query, user_id)

    # ── Service selection ─────────────────────────────────
    elif data.startswith("service_"):
        date_index = int(data.replace('service_',''))
        service = Config.SERVICES[date_index]
        booking['service'] = service
        booking['state'] = SELECTING_DATE

        logger.info(f"Service selected: {service}")

        await edit_message_text(
            f"✅ Service *{service}*\n\n"
            "Please select a date:",
            reply_markup=date_keyboard(),
            parse_mode='Markdown'
        )
       
    # ── Date selection ──────────────────────────────────── 
    elif data.startswith('date_'):
        date_value = data.replace('date_','')
        booking['date'] = date_value
        booking['state'] = SELECTING_TIME

        # Get display date from available dates
        dates = get_available_dates()
        for date in dates:
            if date['value'] == date_value:
                booking['date_display'] = date['display']
                break

        logger.info(f"Date selected: {date_value}")

        await query.edit_message_text(
            f"✅ Service: *{booking['service']}*\n"
            f"✅ Date: *{booking['date_display']}*\n\n"
            "Please select a time slot:\n"
            "🟢 Available 🔴 Booked",
            reply_markup=time_keyboard(date_value),
            parse_mode='Markdown'
        )

    # ── Time slot selection ───────────────────────────────
    elif data.startswith('time_'):
        time_index = int(data.replace('time_',''))
        time_slot = Config.TIME_SLOTS[time_index]
        booking['time_slot'] = time_slot
        booking['state'] = WAITING_NAME

        logger.info(f"Time selected: {time_slot}")

        await query.edit_message_text(
            f"✅ Service *{booking['service']}*\n"
            f"✅ Date *{booking['date_display']}*\n"
            f"✅ Time: *{time_slot}*\n\n"
            "Please enter your *full name*:",
            parse_mode='Markdown'
        )
    
    elif data == 'slot_taken':
        await query.answer('This slor is already booked. Please choose another.', show_alert=True)

    # ── Back buttons ──────────────────────────────────────
    elif data == 'back_main':
        booking['state'] = SELECTING_ACTION
        await query.edit_messsage_text(
            'How can i help you today?',
            reply_markup = main_menu_keyboard()
        )
    elif data == 'back_service':
        booking['state'] = SELECTING_SERVICE
        await query.edit_message_text(
            'Please select a service:',
            reply_markup = service_keyboard()
        )
    elif data == 'back_date':
        booking['state'] = SELECTING_DATE
        await query.edit_message_text(
            f"✅ Sevice *{booking['service']}*\n\n"
            'Please select a date:',
            reply_markup = date_keyboard(),
            parse_mode='Markdown'
        )

    # ── Cancel specific appointment ───────────────────────
    elif data.startswith('cancel_'):
       appointment_id = int(data.replace('cancel_',''))
       success = cancel_appointment(appointment_id, user_id)

       if success:
           await query.edit_message_text(
               f'✅ Your appointment has been cancelled successfully.\n\n'
               'Type /start to book a new appointment.'
           )
    else:
        await query.edit_message_text('❌ Could not cancel appointment. Please try again.')

# ── Message handler ───────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id=update.effective_chat.id
    text = update.message.text.strip()
    booking = get_user_data(context)
    state = booking['state']

    await context.bot.send_chat_action(
        chat_id=chat_id,
        action='typing'
    )
    
    if state == WAITING_NAME:
        await handle_name(update, context, booking, text)
    elif state == WAITING_PHONE:
        await handle_phone(update, context, booking, text, user.id)
    else:
        await update.message.reply_text(
            "Please use the menu to naviagate.\n"
            "Type /start to see the main menu."
        )

# ── Name input ────────────────────────────────────────────
async def handle_name(update, context, booking, text):
    if not validate_name(text):
        await update.message.reply_text(
            "❌ Please enter a valid name.\n"
            "Example: *John Smith*",
            parse_mode='Markdown'
        )
        return
    
    booking['name'] = text
    booking['state'] = WAITING_PHONE

    await update.message.reply_text(
        f"Nice to meet you *{text}*!😊\n\n"
        "Please enter your *phone number*:",
        parse_mode='Markdown'
    )

# ── Phone input ───────────────────────────────────────────
async def handle_phone(update, context, booking, text, user_id):
    if not validate_phone(text):
        await update.message.reply_text(
            "❌ Please enter a valid phone number.\n"
            "Example: *+44 7931 641325* or *1-800-555-0199*",
            parse_mode='Markdown'
        )
        return
    
    booking['state'] = text
    booking['state'] = DONE

    # save patient data
    save_patient(user_id, booking['name'], text)

    # save appointment data
    appointment_id = save_appointment(
        telegram_id=user_id,
        name=booking['name'],
        phone=text,
        service=booking['service'],
        date=booking['state'],
        time_slot=booking['time_slot']      
    )

    if appointment_id:
        logger.info(f"Appointment booked: {booking['name']} - {booking['date']} {booking['time_slot']}")

        await update.message.reply_text(
            f"✅ *Appointment Confirmed!\n\n*"
            f"👤 Name: {booking['name']}\n"
            f"📱 Phone: {text}\n"
            f"🏥 Service: {booking['service']}\n"
            f"📅 Date: {booking['date']}\n"
            f"🕐 Time: {booking['time_slot']}"
            f"We'll send you reminder 1 hour before.\n"
            f"See you soon! 🙌",
            parse_mode='Markdown'
        )

        # Notify admin
        await notify_admin(context, booking, user_id, appointment_id)

    else:
        await update.message_reply_text(
            "⚠️ Something went wrong. Please try again with /start"
        )

# ── Show user appointments ────────────────────────────────
async def show_appointments(query, user_id: int):
    appointments = get_user_appointment(user_id)

    if not appointments:
        await query.edit_message_text(
            "You have no upcoming appointments.\n\n"
            "Type /start to book one!"
        )
        return
    
    msg = "📋 *Your upcoming Appointments*\n\n"
    for appointment in appointments:
        msg += (
            f"🔹 *{appointment['service']}*\n"
            f"  📅 {appointment['date']}\n"
            f"  🕐 {appointment['time_slot']}\n"
            f"  🆔 Booking ID: `{appointment['id']}`"
        )

        await query.edit_message_text(msg, parse_mode='Markdown')

# ── Show cancel options ───────────────────────────────────
async def show_cancel_options(query, user_id: int):
    appointments = get_user_appointment(user_id)

    if not appointments:
        await query.edit_message_text(
            'You have no appointments to cancel.\n\n'
            'Type /start to book one!'
        )
        return

    keyboard = []
    for appointment in appointments:
        keyboard.append([
            InlineKeyboardButton(f"❌{appointment['service']} - {appointment['date']} {appointment['time_slot']}", callback_data=f"cancel_{appointment['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back_main')])

    await query.edit_message_text(
        "Which appointment would you like to cancel?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ── Admin notification ────────────────────────────────────
async def notify_admin(context, booking: dict, user_id: int, appointment_id: int):
    try:
        message = (
            f"🔔 *New Appointment Booked!*\n\n"
            f"👤 Name: {booking['name']}\n"
            f"📱 Phone: {booking['phone']}\n"
            f"🏥 Service: {booking['service']}\n"
            f"📅 Date: {booking['date_display']}\n"
            f"🕐 Time: {booking['time_slot']}\n"
            f"🆔 Booking ID: `{appointment_id}`\n"
            f"👤 Telegram ID: `{user_id}`"
        )
        await context.bot.send_message(
            chat_id=Config.ADMIN_ID,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Admin notified about new appointment")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")
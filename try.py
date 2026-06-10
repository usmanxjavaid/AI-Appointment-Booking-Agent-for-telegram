from telegram import InlineKeyboardMarkup, InlineKeyboardButton
def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = []

    keyboard.append([InlineKeyboardButton('My appointment', callback_data='action_appointment')])

    return InlineKeyboardMarkup(keyboard)

print(main_menu_keyboard())
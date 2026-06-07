import sqlite3
import os
from datetime import datetime
from core.logger import logger

DB_FILE = "database.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    # Rows behave like dictionaries
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates all tables when bot starts"""
    conn = get_connection()
    cursor = conn.cursor()

    # Patients table - stores user info
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            phone TEXT,
            created_at TEXT
                   )
    ''')
    # Appointment table - stores all bookings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            name TEXT,
            phone TEXT,
            service TEXT,
            date TEXT,
            time_slot TEXT,
            status TEXT DEFAULT 'confirmed',
            reminder_sent INTEGER DEFAULT 0,
            created_at TEXT
                   )
                   ''')
    
    # status options:
    # confirmed -> appointment is booked
    # cancellerd -> user cancelled appointment
    # completed -> appointment done

    # reminder_sent
    # 0 -> reminder not sent yet
    # 1 -> reminder already sent

    conn.commit()
    conn.close()
    logger.info(f"Database Initialized")

def save_patient(telegram_id: int, name: str, phone: str):
    """Saves patient info"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO patients
            (telegram_id, name, phone, created_at)
            VALUES (?, ?, ?, ?)
        ''',(telegram_id, name, phone, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        logger.info(f"Patient saved: {name}")
    except Exception as e:
        logger.error(f"Failed to save patient: {e}")
    finally:
        conn.close()

def save_appointment(telegram_id: int, name: str, phone: str,
                     service: str, date: str, time_slot: str) -> int:
    """
    Saves appointment and returns appointment ID.
    We return ID so we can reference it later for reminders/cancellation.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO appointments
            (telegram_id, name, phone, service, date,
            time_slot, status, reminder_sent, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'confirmed', 0, ?)
        ''', (telegram_id, name, phone, service, date, time_slot,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        appointment_id = cursor.lastrowid
        logger.info(f"Appointment saved: {name} - {date} {time_slot}")
        return appointment_id
    except Exception as e:
        logger.error(f"Failed to save appointment: {e}")
        return None
    finally:
        conn.close()

def is_slot_available(date:str, time_slot: str) -> bool:
    """
    Checks if a time slot is already booked.
    Returns True if slot is free, False if taken
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM appointments
        WHERE date = ? AND time_slot = ? AND status = 'confirmed'
    ''', (date, time_slot))
    count = cursor.fetchone()[0]
    conn.close()
    return count == 0 # True if no bookings for this slot

def get_user_appointment(telegram_id:int) -> list:
    """Returns all upcoming appointments for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM appointments
        WHERE telegram_id = ? and status = 'confirmed'
        ORDER BY date ASC, time_slot ASC
    ''', (telegram_id,))
    appointments = cursor.fetchall()
    conn.close()
    return appointments

def cancel_appointment(appointment_id: int, telegram_id: int) -> bool:
    """
    Cancels an appointment.
    We check telegram_id too so users can only cancel their own appointments.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE appointments SET status = 'cancelled'
            WHERE id = ? AND telegram_id = ?
        ''', (appointment_id, telegram_id))
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            logger.info(f"Appointment {appointment_id} cancelled")
            return success
    except Exception as e:
        logger.error(f"Failed to cancel appointment: {e}")
        return False
    finally:
        conn.close()


def get_all_appointments() -> list:
    """Returns all appointments for admin"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(''''
        SELECT * FROM appointments
        ORDER BY date ASC, time_slot ASC
                   ''')
    appointments = cursor.fetchall()
    conn.close()
    return appointments
    
def get_upcoming_reminders() -> list:
    """
    Returns appointments that need reminders sent.
    Used by scheduler to send reminders automatically.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM appointments
        WHERE status = 'confirmed' AND reminder_sent = 0
    ''')
    appointments = cursor.fetchall()
    conn.close()
    return appointments

def mark_reminder_sent(appointment_id: int):
    """Marks reminder as sent so we don't send it twice"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE appointments SET reminder_sent = 1
        WHERE id = ?
    ''', (appointment_id,))
    conn.commit()
    conn.close()

def get_stats() -> dict:
    """Returns statistics for admin panel"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM appointments')
    total_appointments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'confirmed'")
    confirmed = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM appointments WHERE status = "cancelled"')
    cancelled = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM patients')
    total_patients = cursor.fetchone()[0]

    conn.close()
    return {
        "total_appointments": total_appointments,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "total_patients": total_patients
    }
  
from groq import Groq
from core.logger import logger
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)

def get_ai_reply(user_message: str, context_info: str = "") -> str:
    """
    Gets AI reply for user message.
    context_info = current booking state so AI knows where user is
    """
    try:
        system_prompt = f"""You are {Config.AGENT_NAME}, a friendly appointment assistant for {Config.COMPANY_NAME}.

Our services: {', '.join(Config.SERVICES)}
Working days: {', '.join(Config.WORKING_DAYS)}
Working hours: 9:00 AM to 5:00 PM

Your job:
- Help patients book appointments
- Answer questions about our clinic and services
- Be friendly and concise — under 80 words
- If patient wants to book, tell them to use the booking menu
- If you don't know something, say so honestly

Current context: {context_info if context_info else 'User just started'}"""

        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150
        )

        reply = response.choices[0].message.content.strip()

        if not reply:
            return "I didn't quite understand that. Could you rephrase?"

        return reply

    except Exception as e:
        logger.error(f"AI reply failed: {e}")
        return "I'm having a technical issue. Please try again."
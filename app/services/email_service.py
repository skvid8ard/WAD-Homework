import random
import string
import logging

logger = logging.getLogger(__name__)

def generate_verification_code(length: int = 6) -> str:
    """Генерация случайного кода для верификации email"""
    alphabet = string.digits
    return ''.join(random.SystemRandom().choice(alphabet) for _ in range(length))

async def send_verification_email(email: str, verification_code: str):
    """
    Заглушка отправки письма с кодом верификации на указанный email
    """
    
    message = f"Ваш код подтверждения регистрации: {verification_code}. Он будет действителен в течение 10 минут."

    print(f"\n{'='*50}")
    print(f"📧 MOCK EMAIL SENDER")
    print(f"To: {email}")
    print(f"Subject: Подтверждение регистрации")
    print(f"Body: {message}")
    print(f"{'='*50}\n")
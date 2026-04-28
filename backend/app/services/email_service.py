import random
import string
import logging
from email.message import EmailMessage
import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)

def generate_verification_code(length: int = 6) -> str:
    """Генерация случайного кода для верификации email"""
    alphabet = string.digits
    return ''.join(random.SystemRandom().choice(alphabet) for _ in range(length))

async def send_verification_email(email: str, verification_code: str):
    """
    Отправка реального письма с кодом через SMTP.
    Если SMTP_USER не настроен, делает fallback и просто выводит код в консоль.
    """
    subject = "Подтверждение регистрации (WAD Chat)"
    body = (
        f"Добро пожаловать!\n\n"
        f"Ваш код подтверждения регистрации: {verification_code}\n\n"
        f"Он будет действителен в течение 10 минут."
    )

    # 1. FALLBACK: Если креды не заданы в .env, выводим в консоль
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print(f"\n{'='*50}")
        print(f"📧 MOCK EMAIL SENDER (SMTP не настроен)")
        print(f"To: {email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print(f"{'='*50}\n")
        return

    # 2. РЕАЛЬНАЯ ОТПРАВКА
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM_EMAIL or "noreply@wadchat.com"
    message["To"] = email
    message["Subject"] = subject
    message.set_content(body)

    try:
        # Асинхронное подключение и отправка (не блокирует Event Loop FastAPI)
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=(settings.SMTP_PORT == 465),   # Порт 465 использует неявный TLS
            start_tls=(settings.SMTP_PORT == 587), # Порт 587 использует STARTTLS
        )
        logger.info(f"✅ Успешно отправлен код подтверждения на {email}")
    except Exception as e:
        logger.error(f"❌ Ошибка SMTP при отправке на {email}: {str(e)}")
        # Кидаем ошибку дальше, чтобы бэкенд вернул 500 ошибку фронтенду,
        # иначе пользователь будет бесконечно ждать письмо, которое не отправилось.
        raise RuntimeError("Не удалось отправить email. Попробуйте позже.")
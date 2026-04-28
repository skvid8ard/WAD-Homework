import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

class EmailService:
    @staticmethod
    async def send_verification_code(email: str, code: str):
        
        message = MIMEText(f"Ваш код подтверждения: {code}")
        message["Subject"] = "Код верификации"
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = email

        try:
            # Используем контекстный менеджер для автоматического закрытия соединения
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.starttls() # Шифруем соединение
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
            print(f"✅ Email успешно отправлен на {email}")
        except Exception as e:
            print(f"❌ Ошибка отправки Email: {e}")
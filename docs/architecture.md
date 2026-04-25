Детализация слоев (Справочник методов)

1. app/core/ (Ядро и Инфраструктура)
config.py: Класс Settings (Pydantic BaseSettings). Читает .env. Добавлены настройки OAuth2 (Google & GitHub).
base.py: DeclarativeBase для SQLAlchemy.
database.py: Асинхронный движок (AsyncEngine), AsyncSessionLocal, зависимость get_db.
redis.py: Глобальный пул redis_client с decode_responses=True.
security.py:
verify_password, get_password_hash (Argon2id).
create_access_token, create_refresh_token (JWT с вшитым jti).
get_auth_cookie_params (Настройки HttpOnly кук).
dependencies.py: get_current_user (Проверка токена, каст UUID, возврат модели User).

2. app/services/ (Бизнес-логика)
- user_service.py (Работа с БД): get_user_by_email, get_user_by_login, create_user, mark_user_as_verified, get_oauth_account, create_oauth_account, create_user_from_oauth (Автогенерация username с защитой от коллизий).
oauth_providers.py (Внешние интеграции OAuth2): GoogleOAuthProvider, GitHubOAuthProvider (Обмен code на access_token, получение профиля, обработка таймаутов, декодирование URL).
- session_service.py (Работа с Redis): save_otp_code, verify_and_delete_otp, save_refresh_session, is_session_valid, delete_refresh_session, revoke_all_user_sessions.
- email_service.py (Внешние интеграции): generate_verification_code, send_verification_email (Mock консоль).
- auth_service.py (Фасад/Оркестратор): register_user, verify_user_email, login_user, refresh_session, logout_user, resend_verification_code, oauth_login (Реализует Implicit Linking и переиспользует логику генерации JWT/jti).
- llm_service.py (Интеграция ИИ): LocalLLMService. Реализует паттерн Singleton для единоразовой загрузки модели `llama-cpp-python`. Содержит методы `generate_response_stream_with_context` для потоковой генерации (SSE) в отдельном потоке (asyncio.to_thread).
- chat_service.py (Работа с БД): create_chat, get_user_chats, get_chat_by_id, get_chat_messages, add_message. Обеспечивает CRUD операции и защиту от IDOR.

3. app/controllers/auth.py (Эндпоинты)
POST /register (JSON: UserCreate) -> 201 Created
POST /verify-email (JSON: VerifyEmailRequest) -> 200 OK
POST /login (OAuth2PasswordRequestForm) -> 200 OK (access_token + Set-Cookie refresh_token)
POST /oauth/{provider}/login (JSON: OAuthLoginRequest) -> 200 OK (access_token + Set-Cookie refresh_token)
POST /refresh (Cookie) -> 200 OK
POST /resend-code (JSON: ResendCodeRequest) -> 200 OK
POST /logout (Защищен токеном) -> 200 OK

4. app/models/ (SQLAlchemy модели)
oauth_account.py: Модель OAuthAccount (Связь 1-ко-многим с User). Хранит provider, account_id и account_email. Уникальное ограничение на связку (provider, account_id).

5. app/controllers/chat.py
POST /chats (JSON: ChatCreate) -> 201 Created (Создание комнаты)
GET /chats -> 200 OK (Список комнат юзера)
GET /chats/{chat_id}/messages -> 200 OK (История диалога)
POST /chats/{chat_id}/messages (JSON: ChatMessageRequest) -> 200 OK (Стриминг ответа от LLM + автосохранение истории в БД)

## Frontend Architecture (React + Vite)
Архитектура фронтенда построена на базе модульной структуры, вдохновленной Feature-Sliced Design (FSD).

6. frontend/src/ (Клиентское приложение)
   - `main.tsx`: Точка входа в React-приложение, монтирование в DOM.
   - `App.tsx`: Главный компонент маршрутизации (React Router).
   - `index.css`: Глобальные стили и инициализация Tailwind CSS v4.
   
   - `widgets/`: Крупные, самостоятельные блоки интерфейса.
     - `Layout.tsx`: Обертка приложения (Sidebar + Main Content Outlet), управление переключением темной/светлой темы.
     
   - `pages/`: Компоненты-страницы, которые привязываются к маршрутам.
   - `shared/`: Общие переиспользуемые элементы (API-клиенты, UI-кит, глобальные сторы).
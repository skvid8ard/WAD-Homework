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

### 5. Сторонние библиотеки (Frontend)
- **react-hot-toast**: Система всплывающих уведомлений.
- **react-markdown + remark-gfm**: Парсинг и рендер Markdown.
- **react-syntax-highlighter**: Подсветка синтаксиса кода.
- **framer-motion**: Анимации интерфейса.
- **lucide-react**: Сет иконок.

6. frontend/src/ (Клиентское приложение)
   - `main.tsx`: Точка входа в React-приложение, монтирование в DOM.
   - `App.tsx`: Главный компонент маршрутизации (React Router).
   - `index.css`: Глобальные стили и инициализация Tailwind CSS v4.
   
   - `widgets/`: Крупные, самостоятельные блоки интерфейса.
     - `Layout.tsx`: Обертка приложения (Sidebar + Main Content Outlet), управление переключением темной/светлой темы.
     
   - `pages/`: Компоненты-страницы, которые привязываются к маршрутам.
   - `shared/`: Общие переиспользуемые элементы (API-клиенты, UI-кит, глобальные сторы).

### 1. Shared Layer (Общие ресурсы)
- **api.ts**: Инстанс Axios. 
  - Настроен `withCredentials: true` для передачи Refresh-куки.
  - Содержит `Request Interceptor` для подстановки Access Token.
  - Содержит `Response Interceptor` для автоматического Silent Refresh при 401 ошибке.
- **store/authStore.ts**: Глобальное состояние (Zustand + Persist).
  - Хранит `accessToken` и флаг `isAuthenticated`.
  - Синхронизирован с `localStorage`.
- **components/ProtectedRoute.tsx**: Компонент-страж. Блокирует доступ к приложению для неавторизованных пользователей.
- **api.ts**: Инстанс Axios с интерцепторами для Silent Refresh.
- **store/authStore.ts**: Состояние авторизации (`accessToken`, функция `logout`).
- **store/themeStore.ts**: Глобальное состояние темы (`isDark`), синхронизированное с классом `.dark` на `<html>` и `localStorage`.
- **store/chatStore.ts**: Глобальное состояние бокового меню (список чатов, загрузка истории, функция очистки при логауте).
- **components/ProtectedRoute.tsx**: Компонент-страж (редирект неавторизованных на `/login`).
- **components/VerificationForm.tsx**: Переиспользуемый UI-компонент ввода OTP кода.
- **components/MarkdownMessage.tsx**: Безопасный рендерер Markdown с поддержкой подсветки синтаксиса (через `react-markdown` и `react-syntax-highlighter`).
- **components/ThemeToggle.tsx**: Кнопка переключения светлой/темной темы.
- **components/PublicRoute.tsx**: Компонент-страж, ограничивающий доступ к публичным страницам (Login/Register) для уже авторизованных пользователей.
- **api.ts (fetchWithAuth)**: Кастомная обертка над Fetch API для SSE-стриминга. Инкапсулирует логику внедрения JWT и автоматического сайлент-рефреша токенов (повторения запроса при 401 ошибке) независимо от Axios.

### 2. Widgets Layer (Крупные блоки)
- **Layout.tsx**: Обертка приложения (Sidebar + Content). Управляет темой и структурой страницы.

### 3. Pages Layer (Страницы)
- **Login.tsx**: Страница входа. Использует `URLSearchParams` для OAuth2 совместимости с FastAPI.
- **Register.tsx**: Двухэтапная регистрация (Данные -> OTP Верификация) с логикой повторной отправки кода (Resend Code).

### Auth Flow (Silent Refresh)
1. **Initial Login**: Пользователь получает `access_token` (JSON) и `refresh_token` (HttpOnly Cookie).
2. **State Management**: Zustand хранит `access_token` и статус `isAuthenticated`.
3. **Axios Interceptor**: 
   - На каждый запрос подкладывает `Authorization: Bearer <token>`.
   - Если получает `401`, блокирует выполнение текущего кода, запрашивает новый токен через `/auth/refresh`.
   - В случае успеха обновления — повторяет исходный запрос.
   - В случае неудачи (кука протухла) — вызывает `authStore.logout()`, принудительно перенаправляя на `/login`.

### 4. Интеграция потоков (Streams API)
В то время как стандартные REST запросы обрабатываются через `axios` (`api.ts`), эндпоинт отправки сообщений (`POST /chats/{id}/messages`) использует нативный **Fetch API + Streams (getReader)** для чтения Server-Sent Events без буферизации, обеспечивая потоковую генерацию ответа в реальном времени.

### ПЛАНИРУЕТСЯ!
### 6. Инфраструктурный слой (Infrastructure)
- **Reverse Proxy**: Nginx выступает в роли "входных ворот". Он терминирует SSL-трафик, отдает статику фронтенда и перенаправляет API-запросы.
- **Volumes**: Персистентность данных обеспечивается через Docker Volumes (для PostgreSQL данных и Redis). 
- **AI Models Storage**: Веса моделей вынесены в отдельную внешнюю директорию, пробрасываемую в контейнер через Mount, чтобы не раздувать размер Docker-образа.
- **Environment Management**: Проект разделен на `development` и `production` конфиги. Секретные ключи (OAuth secrets, DB passwords) передаются строго через переменные окружения, исключая их попадание в репозиторий.
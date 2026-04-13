# WAD-Homework
backend/
├── app/
│   ├── core/           # Настройки, инициализация БД, Redis, безопасность
│   ├── models/         # SQLAlchemy модели (Model)
│   ├── schemas/        # Pydantic модели для валидации ввода/вывода
│   ├── services/       # Бизнес-логика (Service)
│   ├── controllers/    # API Роутеры (Controller)
│   └── main.py         # Точка входа приложения
├── .env                # Переменные окружения
└── requirements.txt

`openssl rand --hex 32`
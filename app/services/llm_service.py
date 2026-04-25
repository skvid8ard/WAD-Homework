import asyncio
from llama_cpp import Llama
from app.core.config import settings

class LocalLLMService:
    # Хранение инстанса загруженной модели
    _model: Llama | None = None

    @classmethod
    def initialize(cls):
        """
        Загружает модель в память (Singleton). 
        Вызывается один раз при старте сервера FastAPI.
        """
        if cls._model is None:
            print(f"🧠 Загрузка LLM модели из {settings.LLM_MODEL_PATH}...")
            # Включается verbose=False, чтобы C++ логи не засоряли терминал
            cls._model = Llama(
                model_path=settings.LLM_MODEL_PATH,
                n_ctx=512,
                n_threads=4,
                verbose=False 
            )
            print("✅ Модель успешно загружена в память!")

    @classmethod
    async def generate_response(cls, user_text: str) -> str:
        """
        Принимает текст пользователя, оборачивает в промпт и асинхронно возвращает ответ.
        """
        if cls._model is None:
            raise RuntimeError("LLM модель не инициализирована!")

        messages =[
            {"role": "system", "content": "Ты полезный и краткий AI-ассистент."},
            {"role": "user", "content": user_text}
        ]

        def _generate():
            # 2. Вызываем метод для ЧАТА, а не просто сырую генерацию текста
            return cls._model.create_chat_completion(
                messages=messages,
                max_tokens=30, # Уменьшили до 30 токенов для сверхбыстрого теста!
                temperature=0.7, # Чуть-чуть креативности
            )

        # Ждем выполнения в отдельном потоке
        result = await asyncio.to_thread(_generate)
        
        # 3. Достаем текст из правильного места (структура ответа тут другая)
        answer = result["choices"][0]["message"]["content"]
        return answer.strip()

    @classmethod
    async def generate_response_stream(cls, user_text: str):
        """
        Асинхронный генератор. Возвращает слова по мере их появления.
        """
        if cls._model is None:
            raise RuntimeError("LLM модель не инициализирована!")

        messages =[
            {"role": "system", "content": "Ты полезный и краткий AI-ассистент."},
            {"role": "user", "content": user_text}
        ]

        # Включаем stream=True. Теперь метод возвращает синхронный итератор.
        # Увеличим max_tokens, чтобы ответ был подлиннее!
        stream = cls._model.create_chat_completion(
            messages=messages,
            max_tokens=100, 
            temperature=0.7,
            stream=True 
        )

        # Перебираем кусочки ответа по мере их генерации C++ ядром
        for chunk in stream:
            # Извлекаем сгенерированный текст (часто это 1-2 буквы или целое слово)
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]
                # ВАЖНО: Отдаем управление Event Loop'у FastAPI, 
                # чтобы сервер не зависал и мог обрабатывать запросы других пользователей!
                await asyncio.sleep(0)

    @classmethod
    async def generate_response_stream_with_context(cls, chat_history: list[dict]):
        """
        Потоковая генерация с учетом истории сообщений.
        """
        if cls._model is None:
            raise RuntimeError("LLM модель не инициализирована!")

        messages =[{"role": "system", "content": "Ты полезный и краткий AI-ассистент."}] + chat_history

        stream = cls._model.create_chat_completion(
            messages=messages,
            max_tokens=200, 
            temperature=0.7,
            stream=True # Включаем стриминг
        )

        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]
                await asyncio.sleep(0) # Не блокируем Event Loop
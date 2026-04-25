import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatCreate, ChatResponse, MessageResponse, ChatMessageRequest
from app.services import chat_service
from app.services.llm_service import LocalLLMService

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
    # Защищаем все эндпоинты в этом роутере: доступ только с валидным JWT-токеном
    dependencies=[Depends(get_current_user)]
)

@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_new_chat(
    chat_in: ChatCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создает новый пустой чат."""
    return await chat_service.create_chat(db, user.id, chat_in)

@router.get("", response_model=List[ChatResponse])
async def list_chats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получает список всех чатов текущего пользователя."""
    return await chat_service.get_user_chats(db, user.id)

# @router.post("/ask")
# async def ask_llm(
#     request: ChatMessageRequest,
#     user: User = Depends(get_current_user) # Получаем текущего пользователя (например, чтобы обращаться по имени)
# ):
#     """
#     Отправляет сообщение пользователя локальной нейросети и возвращает ответ.
#     """
#     # Вызываем наш LLM сервис (он работает в отдельном потоке и не блокирует сервер)
#     answer = await LocalLLMService.generate_response(request.message)
    
#     return {
#         "user_id": str(user.id),
#         "answer": answer
#     }

# @router.post("/ask/stream")
# async def ask_llm_stream(
#     request: ChatMessageRequest,
#     user: User = Depends(get_current_user)
# ):
#     """
#     Потоковая генерация ответа от локальной LLM.
#     """
#     # Мы передаем генератор напрямую в StreamingResponse.
#     # media_type="text/event-stream" говорит браузеру (или curl), что данные будут приходить частями.
#     return StreamingResponse(
#         LocalLLMService.generate_response_stream(request.message),
#         media_type="text/event-stream"
#     )

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    chat_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получает историю сообщений конкретного чата."""
    # 1. Защита от IDOR: проверяем, существует ли чат и принадлежит ли он юзеру
    chat = await chat_service.get_chat_by_id(db, chat_id, user.id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Chat not found or access denied / Чат не найден или доступ запрещен"
        )
    
    # 2. Отдаем сообщения
    return await chat_service.get_chat_messages(db, chat_id)

@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: uuid.UUID,
    request: ChatMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Отправляет сообщение в чат, возвращает ответ ИИ в потоке (Streaming) 
    и автоматически сохраняет историю в БД.
    """
    # 1. Защита от IDOR
    chat = await chat_service.get_chat_by_id(db, chat_id, user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 2. Сохраняем сообщение пользователя в БД
    await chat_service.add_message(db, chat_id, "user", request.message)

    # 3. Выгружаем историю сообщений для контекста
    history_records = await chat_service.get_chat_messages(db, chat_id)
    chat_history =[
        {"role": msg.role, "content": msg.content}
        for msg in history_records
    ]

    # 4. Создаем Генератор-Обертку
    async def stream_and_save():
        full_answer = ""
        
        # Получаем куски от LLM
        async for chunk in LocalLLMService.generate_response_stream_with_context(chat_history):
            full_answer += chunk # Склеиваем полный ответ для базы
            yield chunk          # Отдаем кусок клиенту (фронтенду)
        
        # Когда цикл for закончился (генерация завершена), сохраняем полный текст в БД!
        await chat_service.add_message(db, chat_id, "assistant", full_answer)

    # 5. Возвращаем поток клиенту
    return StreamingResponse(stream_and_save(), media_type="text/event-stream")
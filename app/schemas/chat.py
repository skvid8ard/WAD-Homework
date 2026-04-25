import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# То, что присылает фронтенд при создании чата
class ChatCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Название чата")

# То, что мы отдаем фронтенду (уже с ID и датой)
class ChatResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    
    # Разрешаем Pydantic читать данные из SQLAlchemy моделей
    model_config = ConfigDict(from_attributes=True) 

# Оставим твою старую схему, она нам еще пригодится для сообщений
class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str       # "user" или "assistant"
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';
import { MarkdownMessage } from '../shared/components/MarkdownMessage';
import { useAuthStore } from '../shared/store/authStore';
import { api, fetchWithAuth } from '../shared/api';
import { useChatStore } from '../shared/store/chatStore';

// Описываем тип сообщения
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const Chat: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // ID чата из URL (если мы внутри существующего чата)
  const navigate = useNavigate();
  const token = useAuthStore((state) => state.accessToken); // Достаем токен для fetch
  const fetchChats = useChatStore((state) => state.fetchChats);

  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  // Рефы для управления DOM
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Загрузка истории чата или очистка при создании нового
  useEffect(() => {
    // Если мы на главной странице (id = undefined), сбрасываем стейт
    if (!id) {
      setMessages([]);
      setPrompt('');
      return;
    }

    // Если id есть, загружаем историю с бэкенда
    const loadChatHistory = async () => {
      try {
        // Axios сам подставит нужный токен из интерцептора
        const response = await api.get(`/chats/${id}/messages`);
        
        // Ожидаем, что бэкенд вернет массив объектов вида[{ role: 'user', content: '...' }, ...]
        // Если у тебя на бэкенде другие названия полей (например, text вместо content),
        // нам нужно будет сделать здесь маппинг. Пока предполагаем, что всё сходится.
        setMessages(response.data);
      } catch (error) {
        console.error('Ошибка загрузки истории чата:', error);
      }
    };

    loadChatHistory();
  }, [id]); // Запускаем этот хук каждый раз, когда меняется id в URL

  // 1. Авто-скролл вниз при добавлении новых сообщений
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 2. Авто-расширение поля ввода
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Сбрасываем высоту
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`; // Растем до 200px
    }
  };

  // 3. Отправка сообщения по кнопке Enter (без Shift)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 4. ГЛАВНАЯ ФУНКЦИЯ: Отправка и Стриминг
  const sendMessage = async () => {
    if (!prompt.trim() || isStreaming) return;

    const userMessage = prompt.trim();
    setPrompt('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto'; // Возвращаем инпут к 1 строке

    // Сразу рисуем сообщение пользователя и пустую болванку для ответа LLM
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);
    setIsStreaming(true);

    try {
      let currentChatId = id;

      // ШАГ А: Если ID нет (новый чат), сначала создаем комнату в БД
      if (!currentChatId) {
        // Берем первые 30 символов для названия чата
        const chatRes = await api.post('/chats', { title: userMessage.slice(0, 30) });
        currentChatId = chatRes.data.id;
        // Тихо меняем URL, чтобы юзер остался в этой же комнате без перезагрузки
        window.history.replaceState(null, '', `/chats/${currentChatId}`);

        fetchChats();
      }

      // ШАГ Б: Отправляем запрос на генерацию
      // Используем нативный fetch для поддержки потокового чтения (Streams API)
      // Используем нашу "умную" обертку. 
      // Обрати внимание: мы больше не передаем headers руками, она всё сделает сама!
      const response = await fetchWithAuth(`http://localhost:8000/chats/${currentChatId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.body) throw new Error('Нет тела ответа');

      // Подключаемся к потоку
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let assistantContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Декодируем порцию байт в текст
        const chunkText = decoder.decode(value, { stream: true });
        
        // ВАЖНО: Разные бэкенды шлют SSE по-разному.
        // Пока мы предполагаем, что бэкенд просто плюется сырым текстом.
        // (Если он шлет 'data: ...', мы поправим этот кусок после твоего теста).
        assistantContent += chunkText;

        // Обновляем текст ПОСЛЕДНЕГО сообщения в массиве
        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1].content = assistantContent;
          return newMessages;
        });
      }

    } catch (error) {
      console.error('Ошибка генерации:', error);
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].content = '**[Ошибка соединения с сервером]**';
        return newMessages;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="absolute inset-0 flex flex-col">
      
      {/* 1. Лента сообщений - теперь она жестко ограничена по высоте */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-4 py-6">
        <div className="max-w-4xl mx-auto w-full flex flex-col">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[60vh] text-zinc-500 opacity-50">
               <Bot size={48} className="mb-4" />
               <p className="text-lg">Начните новый диалог</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`flex items-start gap-3 mb-6 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0 border border-emerald-500/20">
                    <Bot className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                  </div>
                )}
                
                <div className={`px-4 py-2.5 rounded-2xl max-w-[85%] text-sm md:text-base ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-tr-none shadow-md' 
                    : 'bg-zinc-100 dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 rounded-tl-none border border-zinc-200 dark:border-zinc-800 shadow-sm'
                }`}>
                  {msg.role === 'user' ? (
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                  ) : (
                    <MarkdownMessage content={msg.content || '...'} />
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} className="h-4 w-full" />
        </div>
      </div>

      {/* 2. Зона ввода - всегда прижата к низу */}
      <div className="flex-shrink-0 p-4 bg-white dark:bg-zinc-950 border-t border-zinc-200 dark:border-zinc-800">
        <div className="max-w-4xl mx-auto">
          <div className="relative flex items-end gap-2 bg-zinc-100 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 rounded-2xl p-2 focus-within:ring-2 focus-within:ring-blue-500/30 transition-all shadow-sm">
            <textarea
              ref={textareaRef}
              value={prompt}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder="Спросите меня о чем-нибудь..."
              className="w-full max-h-40 bg-transparent text-zinc-900 dark:text-zinc-100 px-3 py-2 focus:outline-none resize-none scrollbar-hide"
              rows={1}
            />
            <button 
              onClick={sendMessage}
              disabled={!prompt.trim() || isStreaming}
              className="p-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-300 dark:disabled:bg-zinc-800 text-white rounded-xl transition-all active:scale-95 shrink-0 shadow-md"
            >
              {isStreaming ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </div>
          <p className="text-[10px] text-zinc-400 text-center mt-2">
            ИИ может ошибаться. Проверяйте информацию.
          </p>
        </div>
      </div>
    </div>
  );
};
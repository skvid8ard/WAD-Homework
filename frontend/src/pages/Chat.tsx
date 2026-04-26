import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react'; // Проверь, что Loader2 тут!
import { useParams } from 'react-router-dom';
import { MarkdownMessage } from '../shared/components/MarkdownMessage';
import { useChatStore } from '../shared/store/chatStore';
import { api, fetchWithAuth } from '../shared/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const Chat: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const fetchChats = useChatStore((state) => state.fetchChats);

  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 1. Авто-скролл
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isHistoryLoading]);

  // 2. Загрузка истории или очистка
  useEffect(() => {
    if (!id) {
      setMessages([]);
      setPrompt('');
      return;
    }

    const loadChatHistory = async () => {
      setIsHistoryLoading(true);
      try {
        const response = await api.get(`/chats/${id}/messages`);
        setMessages(response.data);
      } catch (error) {
        console.error('Ошибка загрузки истории:', error);
      } finally {
        setIsHistoryLoading(false);
      }
    };

    loadChatHistory();
  }, [id]);

  // 3. Обработка ввода
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 4. Отправка сообщения
  const sendMessage = async () => {
    if (!prompt.trim() || isStreaming) return;

    const userMessage = prompt.trim();
    setPrompt('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);
    setIsStreaming(true);

    try {
      let currentChatId = id;
      if (!currentChatId) {
        const chatRes = await api.post('/chats', { title: userMessage.slice(0, 30) });
        currentChatId = chatRes.data.id;
        window.history.replaceState(null, '', `/chats/${currentChatId}`);
        fetchChats();
      }

      const response = await fetchWithAuth(`http://localhost:8000/chats/${currentChatId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.body) throw new Error('No body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let assistantContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        assistantContent += decoder.decode(value, { stream: true });

        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1].content = assistantContent;
          return newMessages;
        });
      }
    } catch (error) {
      console.error('Streaming error:', error);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="absolute inset-0 flex flex-col bg-white dark:bg-zinc-950 transition-colors duration-300">
      
      {/* ЛЕНТА СООБЩЕНИЙ */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-4 py-6">
        <div className="max-w-4xl mx-auto w-full flex flex-col">
          
          {isHistoryLoading ? (
            <div className="space-y-8 mt-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-zinc-200 dark:bg-zinc-800 animate-pulse shrink-0" />
                <div className="space-y-2 w-full">
                  <div className="h-4 bg-zinc-200 dark:bg-zinc-800 animate-pulse rounded w-3/4" />
                  <div className="h-4 bg-zinc-200 dark:bg-zinc-800 animate-pulse rounded w-1/2" />
                </div>
              </div>
              <div className="flex items-start gap-3 justify-end">
                <div className="space-y-2 w-full flex flex-col items-end">
                  <div className="h-4 bg-zinc-200 dark:bg-zinc-800 animate-pulse rounded w-2/3" />
                  <div className="h-4 bg-zinc-200 dark:bg-zinc-800 animate-pulse rounded w-1/3" />
                </div>
                <div className="w-8 h-8 rounded-full bg-zinc-200 dark:bg-zinc-800 animate-pulse shrink-0" />
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[60vh] text-zinc-500 opacity-50">
              <Bot size={48} className="mb-4" />
              <p className="text-lg font-medium">Начните новый диалог</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`flex items-start gap-3 mb-6 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0 border border-emerald-500/20 text-emerald-500">
                    <Bot size={20} />
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
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center shrink-0 border border-blue-500/20 text-blue-500">
                    <User size={20} />
                  </div>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} className="h-4 w-full" />
        </div>
      </div>

      {/* ЗОНА ВВОДА */}
      <div className="flex-shrink-0 p-4 bg-white dark:bg-zinc-950 border-none ">
        <div className="max-w-4xl mx-auto">
          <div className="relative flex items-end gap-2 bg-zinc-100 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 rounded-2xl p-2 focus-within:ring-2 focus-within:ring-blue-500/30 transition-all shadow-sm">
            <textarea
              ref={textareaRef}
              value={prompt}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder="Спросите меня о чем-нибудь..."
              className="w-full max-h-40 bg-transparent text-zinc-900 dark:text-zinc-100 px-3 py-2 focus:outline-none resize-none scrollbar-hide text-sm md:text-base"
              rows={1}
            />
            <button 
              onClick={sendMessage}
              disabled={!prompt.trim() || isStreaming}
              className="p-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-300 dark:disabled:bg-zinc-800 text-white rounded-xl transition-all active:scale-95 shrink-0 shadow-md h-[42px] w-[42px] flex items-center justify-center"
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
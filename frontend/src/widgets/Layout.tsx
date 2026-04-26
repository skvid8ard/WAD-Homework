import { useState, useEffect } from 'react';
import { Outlet, useNavigate, useParams } from 'react-router-dom';
import { MessageSquare, Plus, LogOut, Menu, X } from 'lucide-react';
import { ThemeToggle } from '../shared/components/ThemeToggle';
import { useChatStore } from '../shared/store/chatStore';
import { useAuthStore } from '../shared/store/authStore';
import { api } from '../shared/api';

export default function Layout() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { chats, fetchChats, isLoading, clearChats } = useChatStore();
  const logout = useAuthStore((state) => state.logout);
  
  // НОВЫЙ СТЕЙТ: Управление мобильным меню
  const[isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  const handleNewChat = () => {
    navigate('/');
    setIsSidebarOpen(false); // Закрываем меню на телефоне после клика
  };

  const handleChatSelect = (chatId: string) => {
    navigate(`/chats/${chatId}`);
    setIsSidebarOpen(false); // Закрываем меню на телефоне после выбора чата
  };

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Ошибка логаута на сервере:', error);
    } finally {
      clearChats();
      logout();
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-white dark:bg-zinc-950 transition-colors duration-300">
      
      {/* 1. OVERLAY (Темный фон для мобилок при открытом меню) */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* 2. SIDEBAR (Адаптивный) */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 flex flex-col bg-zinc-50 dark:bg-zinc-950 border-r border-zinc-200 dark:border-zinc-800 transition-transform duration-300 ease-in-out
        md:relative md:translate-x-0
        ${isSidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}
        shadow-xl /* Добавили тень */
      `}>
        {/* Кнопка закрытия внутри сайдбара (только для мобилок) */}
        <div className="flex justify-between items-center p-4 md:hidden">
          <span className="font-bold text-zinc-900 dark:text-white">Меню</span>
          <button 
            onClick={() => setIsSidebarOpen(false)}
            className="p-2 rounded-lg text-zinc-500 hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-4 pt-2 md:pt-4">
          <button 
            onClick={handleNewChat}
            className="flex items-center gap-2 w-full py-2.5 px-4 bg-zinc-200 hover:bg-zinc-300 dark:bg-zinc-800/80 dark:hover:bg-zinc-700 text-zinc-900 dark:text-zinc-100 rounded-lg font-medium shadow-sm transition-all duration-200 active:scale-[0.98]"
          >
            <Plus size={18} />
            <span>Новый чат</span>
          </button>
        </div>

        {/* Список чатов */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1 scrollbar-hide">
          {isLoading ? (
            <div className="text-center text-sm text-zinc-500 py-4">Загрузка...</div>
          ) : chats.length === 0 ? (
            <div className="text-center text-sm text-zinc-500 py-4">Нет истории чатов</div>
          ) : (
            chats.map((chat) => (
              <button 
                key={chat.id}
                onClick={() => handleChatSelect(chat.id)}
                className={`flex items-center gap-3 w-full p-3 text-left rounded-lg transition-colors ${
                  id === chat.id 
                    ? 'bg-zinc-200/80 dark:bg-zinc-800/80 text-zinc-900 dark:text-zinc-100' 
                    : 'hover:bg-zinc-100 dark:hover:bg-zinc-800/50 text-zinc-600 dark:text-zinc-300'
                }`}
              >
                <MessageSquare size={18} className="text-zinc-500 dark:text-zinc-400 shrink-0" />
                <span className="truncate text-sm font-medium">{chat.title || 'Новый чат'}</span>
              </button>
            ))
          )}
        </div>

        {/* Низ сайдбара */}
        <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 flex justify-between items-center text-zinc-500 dark:text-zinc-400">
          <ThemeToggle />
          <button 
            onClick={handleLogout}
            className="p-2 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-lg text-red-500 transition-all duration-200 active:scale-95"
            title="Выйти из аккаунта"
          >
            <LogOut size={20} />
          </button>
        </div>
      </aside>

      {/* 3. ОСНОВНОЙ КОНТЕНТ (Чат) */}
      <main className="flex-1 flex flex-col min-w-0 h-screen bg-white dark:bg-zinc-950">
        
        {/* Мобильная шапка (Header) - видна только на маленьких экранах */}
        <header className="md:hidden flex items-center p-4 border-b border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md z-30 relative">
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 -ml-2 mr-2 rounded-lg text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
          >
            <Menu size={24} />
          </button>
          <span className="font-semibold text-zinc-900 dark:text-white truncate">
            {chats.find(c => c.id === id)?.title || 'Новый чат'}
          </span>
        </header>

        {/* Outlet (содержимое Chat.tsx) */}
        <div className="flex-1 relative min-h-0">
          <Outlet />
        </div>
        
      </main>
    </div>
  );
}
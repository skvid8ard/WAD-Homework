import { useEffect } from 'react';
import { Outlet, useNavigate, useParams } from 'react-router-dom';
import { MessageSquare, Plus, LogOut } from 'lucide-react';
import { ThemeToggle } from '../shared/components/ThemeToggle';
import { useChatStore } from '../shared/store/chatStore';
import { useAuthStore } from '../shared/store/authStore';
import { api } from '../shared/api';

export default function Layout() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>(); // Получаем ID текущего чата из URL
  
  // Достаем данные и функцию загрузки из нашего нового стора
  const { chats, fetchChats, isLoading } = useChatStore();

  // Загружаем чаты при первой отрисовке Layout (когда юзер залогинился)
  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  // Функция для кнопки "Новый чат"
  const handleNewChat = () => {
    navigate('/'); // Кидаем на главную страницу (пустой чат)
  };

  const logout = useAuthStore((state) => state.logout);
  // Достаем функцию очистки чатов из chatStore, который мы уже импортировали ранее
  const clearChats = useChatStore((state) => state.clearChats); 

  const handleLogout = async () => {
    try {
      // 1. Убиваем сессию на сервере (Redis)
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Ошибка логаута на сервере:', error);
    } finally {
      // 2. В любом случае (даже если сервер недоступен) очищаем локальные данные
      clearChats();
      logout(); // Эта функция поставит isAuthenticated = false
      // ProtectedRoute автоматически перехватит это и перекинет нас на /login
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-64 flex flex-col bg-zinc-50/50 dark:bg-zinc-950/50 border-r border-zinc-200 dark:border-zinc-800 transition-colors duration-300">
        <div className="p-4">
          <button 
            onClick={handleNewChat}
            className="flex items-center gap-2 w-full py-2.5 px-4 bg-zinc-200 hover:bg-zinc-300 dark:bg-zinc-800/80 dark:hover:bg-zinc-700 text-zinc-900 dark:text-zinc-100 rounded-lg font-medium shadow-sm transition-all duration-200 active:scale-[0.98]"
          >
            <Plus size={18} />
            <span>Новый чат</span>
          </button>
        </div>

        {/* Динамический список чатов */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1">
          {isLoading ? (
            <div className="text-center text-sm text-zinc-500 py-4">Загрузка...</div>
          ) : chats.length === 0 ? (
            <div className="text-center text-sm text-zinc-500 py-4">Нет истории чатов</div>
          ) : (
            chats.map((chat) => (
              <button 
                key={chat.id}
                onClick={() => navigate(`/chats/${chat.id}`)}
                // Если ID чата совпадает с URL, подсвечиваем его как активный
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

      <main className="flex-1 flex flex-col relative">
        <Outlet />
      </main>
    </div>
  );
}
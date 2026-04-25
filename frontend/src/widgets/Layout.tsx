import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { MessageSquare, Plus, Sun, Moon, LogOut } from 'lucide-react';

export default function Layout() {
  // Состояние темы. Так как в index.html уже есть "dark", начальное значение - true
  const [isDark, setIsDark] = useState(true);

  // Эффект, который переключает класс на теге <html> при изменении состояния
  useEffect(() => {
    const html = document.documentElement;
    if (isDark) {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  }, [isDark]);

  return (
    <div className="flex h-screen overflow-hidden bg-white dark:bg-zinc-900 transition-colors duration-300">
      
      {/* Левый Сайдбар (Список чатов) */}
      <aside className="w-64 flex flex-col bg-zinc-50 dark:bg-zinc-950 border-r border-zinc-200 dark:border-zinc-800 transition-colors duration-300">
        <div className="p-4">
          <button className="flex items-center gap-2 w-full py-2.5 px-4 bg-zinc-900 dark:bg-white text-white dark:text-black rounded-lg font-medium hover:scale-[1.02] transition-transform shadow-sm">
            <Plus size={18} />
            <span>Новый чат</span>
          </button>
        </div>

        {/* Скелет списка чатов (пока хардкод) */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1">
          <button className="flex items-center gap-3 w-full p-3 text-left rounded-lg bg-zinc-200 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100">
            <MessageSquare size={18} className="text-zinc-500 dark:text-zinc-400" />
            <span className="truncate text-sm font-medium">Как меня зовут?</span>
          </button>
          <button className="flex items-center gap-3 w-full p-3 text-left rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800/50 text-zinc-600 dark:text-zinc-300 transition-colors">
            <MessageSquare size={18} className="text-zinc-500 dark:text-zinc-400" />
            <span className="truncate text-sm font-medium">Проект на React</span>
          </button>
        </div>

        {/* Нижняя часть сайдбара (Настройки/Юзер) */}
        <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 flex justify-between items-center text-zinc-500 dark:text-zinc-400">
          <button 
            onClick={() => setIsDark(!isDark)} 
            className="p-2 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-lg transition-colors"
          >
            {isDark ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          
          <button className="p-2 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-lg transition-colors text-red-500">
            <LogOut size={20} />
          </button>
        </div>
      </aside>

      {/* Правая часть (Основной контент) */}
      <main className="flex-1 flex flex-col relative">
        {/* Компонент Outlet будет динамически заменяться на содержимое страницы */}
        <Outlet />
      </main>

    </div>
  );
}
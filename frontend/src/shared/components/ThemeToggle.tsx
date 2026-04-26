import { useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';
import { useThemeStore } from '../store/themeStore';

export const ThemeToggle = () => {
  const { isDark, toggleTheme } = useThemeStore();

  // Эффект при монтировании: если юзер перезагрузил страницу,
  // мы читаем стейт из localStorage (через Zustand) и применяем класс к HTML
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  },[isDark]);

  return (
    <button 
      onClick={toggleTheme} 
      className="p-2 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-lg transition-colors text-zinc-500 dark:text-zinc-400 transition-all duration-200 active:scale-95"
      title="Переключить тему"
    >
      {isDark ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  );
};
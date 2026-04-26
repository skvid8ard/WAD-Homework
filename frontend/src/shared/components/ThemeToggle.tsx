import { useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';
import { useThemeStore } from '../store/themeStore';

export const ThemeToggle = () => {
  const { isDark, toggleTheme } = useThemeStore();

  // Принудительная синхронизация при каждом изменении isDark
  useEffect(() => {
    const root = window.document.documentElement;
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [isDark]);

  return (
    <button 
      onClick={toggleTheme} 
      className="p-3 bg-zinc-100/50 hover:bg-zinc-200 dark:bg-zinc-800/50 dark:hover:bg-zinc-800 rounded-xl transition-all duration-200 active:scale-90 text-zinc-500 dark:text-zinc-400 backdrop-blur-sm shadow-sm border border-zinc-200/50 dark:border-zinc-700/50"
      aria-label="Toggle theme"
    >
      {isDark ? (
        <Sun size={20} className="text-yellow-500 transition-all" />
      ) : (
        <Moon size={20} className="text-zinc-600 transition-all" />
      )}
    </button>
  );
};
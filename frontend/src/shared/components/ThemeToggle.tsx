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
      className="p-2 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-lg transition-all duration-200 active:scale-95 text-zinc-500 dark:text-zinc-400"
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
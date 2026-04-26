import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeState {
  isDark: boolean;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      isDark: true, // Темная по умолчанию (как в index.html)
      toggleTheme: () => set((state) => {
        const newIsDark = !state.isDark;
        // Сразу мутируем DOM для мгновенного эффекта
        if (newIsDark) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        return { isDark: newIsDark };
      }),
    }),
    {
      name: 'theme-storage', // Сохраняем в localStorage
    }
  )
);
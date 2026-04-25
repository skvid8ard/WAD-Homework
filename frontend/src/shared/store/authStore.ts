import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Описание структуры состояния
interface AuthState {
  accessToken: string | null;
  isAuthenticated: boolean;
  // Действия (actions)
  setToken: (token: string) => void;
  logout: () => void;
}

// Создание хранилища
// Используется middleware 'persist', чтобы access_token сохранялся в localStorage браузера,
// чтобы при обновлении страницы (F5) юзер не вылетал из аккаунта
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      isAuthenticated: false,

      setToken: (token) => set({ accessToken: token, isAuthenticated: true }),
      logout: () => set({ accessToken: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage', // Ключ, под которым данные будут лежать в localStorage
    }
  )
);

if (import.meta.env.DEV) {
    if (window) { (window as any).authStore = useAuthStore; }
}
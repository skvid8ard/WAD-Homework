import axios from 'axios';
import { useAuthStore } from './store/authStore';

// Создание инстанса Axios с базовыми настройками
export const api = axios.create({
  baseURL: 'http://localhost:8000', // Адрес FastAPI бэкенда
  withCredentials: true, // Разрешение отправки HttpOnly кук (refresh_token)
});

// Настройка Request Interceptor (Перехватчик запросов)
// Этот код выполняется автоматически перед отправкой любого запроса через api
api.interceptors.request.use(
  (config) => {
    // Достается токен напрямую из Zustand (вне React-компонента!)
    const token = useAuthStore.getState().accessToken;
    
    // Если токен есть, прикрепляем его в заголовки по стандарту OAuth2
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response, // Если всё ок, просто возвращаем ответ
  async (error) => {
    const originalRequest = error.config;

    // Проверяем: если ошибка 401 и мы еще не пытались обновить токен (защита от бесконечного цикла)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Просим бэкенд выдать новый access_token
        // Бэкенд сам возьмет refresh_token из куки
        const response = await axios.post(
          'http://localhost:8000/auth/refresh',
          {},
          { withCredentials: true }
        );

        const { access_token } = response.data;

        // Сохраняем новый токен в Zustand
        useAuthStore.getState().setToken(access_token);

        // Обновляем заголовок в упавшем запросе и повторяем его
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Если даже рефреш не помог (например, кука протухла через 30 дней)
        // Разлогиниваем пользователя
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

if (import.meta.env.DEV) {
  (window as any).api = api;
}
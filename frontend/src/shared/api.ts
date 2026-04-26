import axios from 'axios';
import { useAuthStore } from './store/authStore';
import toast from 'react-hot-toast';

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

/**
 * Обертка над нативным fetch для поддержки SSE и автоматического обновления токенов.
 * Повторяет логику работы Axios Interceptor.
 */
export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  let token = useAuthStore.getState().accessToken;

  // Функция-хелпер для генерации заголовков с актуальным токеном
  const getHeaders = (currentToken: string | null) => ({
    ...options.headers,
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${currentToken}`
  });

  // 1. Делаем первую попытку запроса
  let response = await fetch(url, {
    ...options,
    headers: getHeaders(token)
  });

  // 2. Если токен протух
  if (response.status === 401) {
    try {
      // Идем за новым токеном (используем наш настроенный axios, чтобы он отправил куки)
      const refreshResponse = await api.post('/auth/refresh');
      const newToken = refreshResponse.data.access_token;

      // Обновляем токен в Zustand
      useAuthStore.getState().setToken(newToken);

      // 3. Повторяем оригинальный fetch-запрос с НОВЫМ токеном
      response = await fetch(url, {
        ...options,
        headers: getHeaders(newToken)
      });
    } catch (error) {
      // Если кука тоже протухла (или ее нет), выкидываем юзера
      useAuthStore.getState().logout();
      throw new Error('Сессия истекла. Пожалуйста, авторизуйтесь заново.');
    }
  }

  return response;
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Проверяем, что это ошибка 401, мы еще не пытались ее повторить (_retry),
    // И САМОЕ ГЛАВНОЕ: это НЕ запрос на логин и НЕ запрос на сам рефреш
    if (
      error.response?.status === 401 && 
      !originalRequest._retry &&
      originalRequest.url !== '/auth/login' &&
      originalRequest.url !== '/auth/refresh'
    ) {
      originalRequest._retry = true; // Ставим флаг, чтобы не уйти в бесконечный цикл

      try {
        // Пытаемся обновить токен
        const response = await api.post('/auth/refresh');
        const newToken = response.data.access_token;

        // Сохраняем новый токен
        useAuthStore.getState().setToken(newToken);

        // Повторяем оригинальный запрос с новым токеном
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
        
      } catch (refreshError) {
        // Если кука тоже протухла, выкидываем юзера
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }

    if (!error.response) {
      toast.error('Ошибка сети. Проверьте подключение к серверу.');
    } else if (error.response.status >= 500) {
      toast.error('Внутренняя ошибка сервера (500).');
    }

    // Если это была ошибка логина - просто возвращаем ее в компонент Login.tsx
    return Promise.reject(error);
  }
);

if (import.meta.env.DEV) {
  (window as any).api = api;
}
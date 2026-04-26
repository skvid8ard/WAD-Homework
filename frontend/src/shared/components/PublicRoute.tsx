import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const PublicRoute = () => {
  const token = useAuthStore((state) => state.accessToken);

  // Если у пользователя есть токен, перенаправляем его на главную (в чаты)
  // replace=true заменяет запись в истории браузера, чтобы юзер не мог вернуться назад по кнопке "Back"
  if (token) {
    return <Navigate to="/" replace />;
  }

  // Если токена нет, показываем дочерние роуты (Login или Register)
  return <Outlet />;
};
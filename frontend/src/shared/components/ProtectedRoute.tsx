import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const ProtectedRoute = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // Если не залогинен — редирект на логин. Если залогинен — показываем контент (Outlet)
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};
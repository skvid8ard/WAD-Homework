import { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../shared/api';
import { useAuthStore } from '../shared/store/authStore';
import toast from 'react-hot-toast';
import { Loader2 } from 'lucide-react';

export const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const setToken = useAuthStore((state) => state.setToken);
  
  // Используем useRef, чтобы предотвратить двойной запрос в React Strict Mode
  const processed = useRef(false);

  useEffect(() => {
    if (processed.current) return;
    
    const code = searchParams.get('code');
    // Предполагаем, что бэкенд вернет нас на /oauth-callback/google или передаст провайдера в URL
    // Давай вытянем провайдера из пути или параметров
    const provider = window.location.pathname.split('/').pop() || 'google';

    if (code) {
      processed.current = true;
      exchangeCode(provider, code);
    } else {
      toast.error('Код авторизации не найден');
      navigate('/login');
    }
  }, []);

  const exchangeCode = async (provider: string, code: string) => {
    try {
      // Отправляем код на бэкенд для обмена на JWT
      const response = await api.post(`/auth/oauth/${provider}/login`, { code });
      
      const { access_token } = response.data;
      setToken(access_token);
      
      toast.success('Успешный вход через соцсеть!');
      navigate('/');
    } catch (error: any) {
      console.error('OAuth Error:', error);
      toast.error(error.response?.data?.detail || 'Ошибка при входе через соцсеть');
      navigate('/login');
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white dark:bg-zinc-950">
      <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
      <h2 className="text-xl font-medium text-zinc-900 dark:text-zinc-100">
        Авторизация...
      </h2>
      <p className="text-zinc-500 text-sm mt-2">Пожалуйста, подождите, мы настраиваем ваш аккаунт</p>
    </div>
  );
};
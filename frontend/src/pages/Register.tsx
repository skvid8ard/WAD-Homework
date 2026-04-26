import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, User, Eye, EyeOff } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../shared/api';
import { ThemeToggle } from '../shared/components/ThemeToggle';
import { VerificationForm } from '../shared/components/VerificationForm';

export const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [resendTimer, setResendTimer] = useState(0);

  const [step, setStep] = useState<1 | 2>(1); // Шаг 1: Регистрация, Шаг 2: Ввод кода
  const[showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const[error, setError] = useState('');
  
  const navigate = useNavigate();

  useEffect(() => {
    if (resendTimer > 0) {
        const timerId = setTimeout(() => setResendTimer(resendTimer - 1), 1000);
        return () => clearTimeout(timerId);
    }
  }, [resendTimer]);

    // 3. Функция отправки повторного кода
    const handleResendCode = async () => {
    if (resendTimer > 0) return; // Если таймер еще идет, ничего не делаем

    setError('');
    try {
        await api.post('/auth/resend-code', { email_or_username: email });
        setResendTimer(60); // Запускаем таймер на 60 секунд
        // Можно добавить уведомление "Код отправлен повторно"
    } catch (err: any) {
        setError(err.response?.data?.detail || 'Не удалось отправить код');
    }
    };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // ВАЛИДАЦИЯ ПАРОЛЕЙ
    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    setIsLoading(true);
    console.log('Попытка регистрации:', { username, email, password });

    try {
      // Отправляем JSON (Axios делает это автоматически, если передать объект)
      await api.post('/auth/register', {
        username,
        email,
        password
      });
      // Если ок, переключаем интерфейс на ввод кода
      setStep(2);
    } catch (err: any) {
      if (err.response?.data?.detail) {
        // Обработка ошибок валидации пароля
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          setError(detail[0].msg || 'Ошибка валидации данных');
        } else {
          setError(detail);
        }
      } else {
        setError('Не удалось подключиться к серверу');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await api.post('/auth/verify-email', {
        email_or_username: email,
        verification_code: otpCode
      });
      // После успешной верификации кидаем на страницу логина
      navigate('/login');
    } catch (err: any) {
      if (err.response?.status === 422) {
        console.log('Детали ошибки 422:', err.response.data.detail);
        setError('Ошибка формата данных. Проверьте консоль.');
      } else {
        setError('Неверный код или ошибка сервера');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 relative">

      {/* Кнопка смены темы в правом верхнем углу */}
      <div className="fixed bottom-6 left-6 z-50 transition-all duration-300">
        <ThemeToggle />
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.85 }} 
        animate={{ opacity: 1, scale: 1 }} 
        transition={{ duration: 0.3 }}
        className="w-full max-w-md bg-white dark:bg-zinc-900 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-zinc-800"
      >
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-6">
          {step === 1 ? 'Создать аккаунт' : 'Подтверждение Email'}
        </h2>

        {error && (
            <div className="p-3 mb-4 text-sm text-red-600 bg-red-50 dark:bg-red-900/30 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800">
              {error}
            </div>
        )}
        
        {/* РЕНДЕРИМ ФОРМУ В ЗАВИСИМОСТИ ОТ ШАГА */}
        {step === 1 ? (
          <form onSubmit={handleRegister} className="space-y-4">
            {/* Имя пользователя */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Имя пользователя (Логин)
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input 
                  type="text" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-zinc-700 rounded-lg bg-gray-50 dark:bg-zinc-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  placeholder="johndoe"
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-zinc-700 rounded-lg bg-gray-50 dark:bg-zinc-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  placeholder="test@example.com"
                  required
                />
              </div>
            </div>

            {/* ПАРОЛЬ 1 */}
            <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Пароль
            </label>
            <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input 
                type={showPassword ? "text" : "password"} 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-12 py-2 border border-gray-300 dark:border-zinc-700 rounded-lg bg-gray-50 dark:bg-zinc-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                placeholder="••••••••"
                required
                />
                <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
                Минимум 8 символов, 1 заглавная буква, 1 цифра и спецсимвол
            </p>
            </div>

            {/* ПОДТВЕРЖДЕНИЕ ПАРОЛЯ */}
            <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Подтвердите пароль
            </label>
            <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input 
                type={showPassword ? "text" : "password"} 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={`w-full pl-10 pr-12 py-2 border rounded-lg bg-gray-50 dark:bg-zinc-800 transition-all outline-none focus:ring-2 focus:ring-blue-500 ${
                    confirmPassword && password !== confirmPassword 
                    ? 'border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 dark:border-zinc-700'
                }`}
                placeholder="••••••••"
                required
                />
                <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
            </div>
            {confirmPassword && password !== confirmPassword && (
                <motion.p 
                initial={{ opacity: 0, y: -10 }} 
                animate={{ opacity: 1, y: 0 }}
                className="text-xs text-red-500 mt-1"
                >
                Пароли не совпадают
                </motion.p>
            )}
            </div>

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 dark:disabled:bg-blue-800 text-white font-medium py-2.5 rounded-lg transition-all duration-200 active:scale-[0.98] flex justify-center items-center mt-2"
            >
              {isLoading ? 'Отправка...' : 'Зарегистрироваться'}
            </button>
          </form>
        ) : (
            <VerificationForm 
                identifier={username} // Передаем email или логин
                otpCode={otpCode}
                setOtpCode={setOtpCode}
                onSubmit={handleVerify}
                onResend={handleResendCode} 
                isLoading={isLoading}
                resendTimer={resendTimer}
                error={error}
                submitText="Подтвердить и войти" // В Register можно не передавать, по умолчанию "Подтвердить"
            />
        )}

        <p className="mt-8 text-center text-sm text-gray-600 dark:text-gray-400">
          Уже есть аккаунт?{' '}
          <Link 
            to="/login" 
            className="font-medium text-blue-600 hover:text-blue-700 dark:text-blue-500 dark:hover:text-blue-400 transition-colors"
          >
            Войти
          </Link>
        </p>
      </motion.div>
    </div>
  );
};
import React from 'react';
import { KeyRound } from 'lucide-react';

// Описываем контракты (какие пропсы принимает наша форма)
interface VerificationFormProps {
  identifier: string; // Сюда передадим email или username, который ввел юзер
  otpCode: string;
  setOtpCode: (code: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onResend: () => void;
  isLoading: boolean;
  resendTimer: number;
  error?: string;
  submitText?: string; // Текст на кнопке (например, "Подтвердить" или "Подтвердить и войти")
}

export const VerificationForm: React.FC<VerificationFormProps> = ({
  identifier,
  otpCode,
  setOtpCode,
  onSubmit,
  onResend,
  isLoading,
  resendTimer,
  error,
  submitText = 'Подтвердить'
}) => {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      {error && (
        <div className="p-3 mb-4 text-sm text-red-600 bg-red-50 dark:bg-red-900/30 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}
      
      <p className="text-sm text-gray-600 dark:text-gray-400 text-center mb-4">
        Мы отправили 6-значный код подтверждения для <span className="font-semibold">{identifier}</span>.
      </p>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Код подтверждения
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <KeyRound className="h-5 w-5 text-gray-400" />
          </div>
          <input 
            type="text" 
            maxLength={6}
            value={otpCode}
            onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))} // Только цифры
            className="w-full text-center tracking-widest text-lg pr-4 py-2 border border-gray-300 dark:border-zinc-700 rounded-lg bg-gray-50 dark:bg-zinc-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            placeholder="000000"
            required
          />
        </div>
      </div>

      <button 
        type="submit" 
        disabled={isLoading || otpCode.length < 6}
        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-400 dark:disabled:bg-green-800 text-white font-medium py-2.5 rounded-lg transition-all duration-200 active:scale-[0.98] mt-2"
      >
        {isLoading ? 'Проверка...' : submitText}
      </button>

      {/* Кнопка повторной отправки (Secondary Button Style) */}
      <div className="text-center mt-6">
        <button
          type="button"
          onClick={onResend}
          disabled={resendTimer > 0 || isLoading}
          className={`text-sm px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
            resendTimer > 0 
              ? 'bg-zinc-100 text-zinc-400 dark:bg-zinc-800/50 dark:text-zinc-500 cursor-not-allowed' 
              : 'bg-zinc-100 hover:bg-zinc-200 text-zinc-700 dark:bg-zinc-800 dark:hover:bg-zinc-700 dark:text-zinc-300 active:scale-95'
          }`}
        >
          {resendTimer > 0 
            ? `Отправить повторно через ${resendTimer}с` 
            : 'Отправить код повторно'}
        </button>
      </div>
    </form>
  );
};
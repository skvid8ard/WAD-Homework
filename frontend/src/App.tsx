import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './widgets/Layout'; 
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ProtectedRoute } from './shared/components/ProtectedRoute';

function ChatPage() {
  return (
    <div className="flex h-full items-center justify-center text-zinc-500 dark:text-zinc-400">
      <h1 className="text-xl">Выберите чат или создайте новый</h1>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 1. Публичный роут (без Сайдбара, на весь экран) */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        {/* 2. Защищенные роуты (внутри Layout с Сайдбаром) */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            {/* Outlet по умолчанию отрендерит ChatPage */}
            <Route index element={<ChatPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
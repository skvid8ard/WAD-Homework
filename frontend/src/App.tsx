import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './widgets/Layout'; 
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ProtectedRoute } from './shared/components/ProtectedRoute';
import { PublicRoute } from './shared/components/PublicRoute';
import { Chat } from './pages/Chat';
import { Toaster } from 'react-hot-toast';
import { OAuthCallback } from './pages/OAuthCallback';

function App() {
  return (
    <>
      {/* 2. Добавляем Toaster в самый корень (с поддержкой темной темы) */}
      <Toaster 
        position="top-center" 
        toastOptions={{
          className: 'bg-white text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100 border border-zinc-200 dark:border-zinc-700 shadow-lg',
        }} 
      />
      
      <BrowserRouter>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/oauth/callback/:provider" element={<OAuthCallback />} />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Layout />}>
              <Route index element={<Chat />} />
              <Route path="chats/:id" element={<Chat />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './widgets/Layout'; 
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ProtectedRoute } from './shared/components/ProtectedRoute';
import { PublicRoute } from './shared/components/PublicRoute';
import { Chat } from './pages/Chat';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        
        {/* Оборачиваем публичные страницы в PublicRoute */}
        <Route element={<PublicRoute />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        {/* Защищенные роуты (без изменений) */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            <Route index element={<Chat />} />
            <Route path="chats/:id" element={<Chat />} />
          </Route>
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './widgets/Layout'; 
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ProtectedRoute } from './shared/components/ProtectedRoute';
import { Chat } from './pages/Chat';

// function ChatPage() {
//   return (
//     <div className="flex h-full items-center justify-center text-zinc-500 dark:text-zinc-400">
//       <h1 className="text-xl">Выберите чат или создайте новый</h1>
//     </div>
//   )
// }

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            {/* Если ID нет - это новый чат */}
            <Route index element={<Chat />} />
            {/* Если ID есть - загрузим историю */}
            <Route path="chats/:id" element={<Chat />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
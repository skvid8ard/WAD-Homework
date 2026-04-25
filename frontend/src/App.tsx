import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './widgets/Layout';

function ChatPage() {
  return (
    <div className="flex-1 flex items-center justify-center text-zinc-500 dark:text-zinc-400">
      <h1 className="text-xl">Выберите чат или создайте новый</h1>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Главный роут оборачивается в Layout */}
        <Route path="/" element={<Layout />}>
          {/* Index route - то, что рендерится внутри Outlet по умолчанию */}
          <Route index element={<ChatPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App;
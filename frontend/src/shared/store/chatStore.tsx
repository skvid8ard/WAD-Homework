import { create } from 'zustand';
import { api } from '../api';

interface ChatItem {
  id: string;
  title: string;
  // Добавим created_at, если он есть в БД, для сортировки (опционально)
}

interface ChatState {
  chats: ChatItem[];
  isLoading: boolean;
  fetchChats: () => Promise<void>;
  clearChats: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  chats:[],
  isLoading: false,
  fetchChats: async () => {
    set({ isLoading: true });
    try {
      // Используем настроенный Axios (api.ts). Он сам подставит токен!
      const response = await api.get('/chats');
      set({ chats: response.data, isLoading: false });
    } catch (error) {
      console.error('Ошибка загрузки чатов:', error);
      set({ isLoading: false });
    }
  },
  clearChats: () => set({ chats: []}),
}));
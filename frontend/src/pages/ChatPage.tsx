// src/pages/ChatsPage.tsx
import React, { useState, useEffect } from 'react';
import { chatService } from '../services/chat';
import { ChatResponse } from '../types/chat';
import { Button } from '../components/ui/Button';

export const ChatsPage: React.FC = () => {
  const [chats, setChats] = useState<ChatResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const loadChats = async () => {
    try {
      const chatsData = await chatService.getMyChats();
      setChats(chatsData);
    } catch (error) {
      console.error('Failed to load chats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadChats();
  }, []);

  if (loading) {
    return <div className="flex justify-center p-8">Загрузка чатов...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto py-6 px-4">
      <h1 className="text-2xl font-bold mb-6">Мои чаты</h1>
      
      <div className="space-y-4">
        {chats.map(chat => (
          <div key={chat.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold">
                  Чат по объявлению: {chat.ad_title}
                </h3>
                <p className="text-sm text-gray-600">
                  Участники: {chat.participant_names.join(', ')}
                </p>
              </div>
              <Button 
                onClick={() => window.location.href = `/chats/${chat.id}`}
                variant="outline"
              >
                Открыть
              </Button>
            </div>
          </div>
        ))}
        
        {chats.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            У вас пока нет чатов
          </div>
        )}
      </div>
    </div>
  );
};
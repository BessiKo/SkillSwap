import React from 'react';
import { useAuth } from '../hooks/useAuth';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Профиль пользователя
          </h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Имя
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {user.first_name} {user.last_name}
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Университет
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {user.university}
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Факультет
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {user.faculty}
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Рейтинг
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {user.rating} ⭐ ({user.total_ratings} оценок)
              </p>
            </div>
          </div>
          
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700">
              О себе
            </label>
            <p className="mt-1 text-sm text-gray-900">
              {user.bio || 'Пользователь пока не добавил информацию о себе'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
// src/pages/DealsPage.tsx
import React, { useState, useEffect } from 'react';
import { dealService } from '../services/deal';
import { DealOut } from '../types/deal';
import { Button } from '../components/ui/Button';

export const DealsPage: React.FC = () => {
  const [deals, setDeals] = useState<DealOut[]>([]);
  const [loading, setLoading] = useState(true);

  const loadDeals = async () => {
    try {
      const dealsData = await dealService.getMyDeals();
      setDeals(dealsData);
    } catch (error) {
      console.error('Failed to load deals:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeals();
  }, []);

  if (loading) {
    return <div className="flex justify-center p-8">Загрузка сделок...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto py-6 px-4">
      <h1 className="text-2xl font-bold mb-6">Мои сделки</h1>
      
      <div className="space-y-4">
        {deals.map(deal => (
          <div key={deal.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold">
                  Сделка #{deal.id}
                </h3>
                <p className="text-gray-600">
                  Объявление: {deal.ad_title}
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                deal.status === 'completed' ? 'bg-green-100 text-green-800' :
                deal.status === 'active' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {deal.status}
              </span>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Предложенная услуга:</span>
                <p>{deal.proposed_service}</p>
              </div>
              <div>
                <span className="font-medium">Желаемая услуга:</span>
                <p>{deal.desired_service}</p>
              </div>
            </div>
          </div>
        ))}
        
        {deals.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            У вас пока нет сделок
          </div>
        )}
      </div>
    </div>
  );
};
// src/pages/AdsPage.tsx
import React, { useState, useEffect } from 'react';
import { adsService } from '../services/ads';
import { AdOut, AdFilter } from '../types/ad';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

export const AdsPage: React.FC = () => {
  const [ads, setAds] = useState<AdOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<AdFilter>({
    page: 1,
    page_size: 20
  });

  const loadAds = async () => {
    try {
      setLoading(true);
      const response = await adsService.getAds(filters);
      setAds(response.items);
    } catch (error) {
      console.error('Failed to load ads:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAds();
  }, [filters]);

  if (loading) {
    return <div className="flex justify-center p-8">Загрузка...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto py-6 px-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Объявления</h1>
        <Button>Создать объявление</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {ads.map(ad => (
          <div key={ad.id} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">{ad.title}</h3>
            <p className="text-gray-600 mb-4">{ad.description}</p>
            <div className="flex justify-between text-sm text-gray-500">
              <span>{ad.category}</span>
              <span>{ad.level}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
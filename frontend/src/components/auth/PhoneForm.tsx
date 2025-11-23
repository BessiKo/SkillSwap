import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

interface PhoneFormProps {
  onCodeSent: (phone: string) => void;
  loading?: boolean;
}

export const PhoneForm: React.FC<PhoneFormProps> = ({ onCodeSent, loading = false }) => {
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!phone.trim()) {
      setError('Введите номер телефона');
      return;
    }

    try {
      await onCodeSent(phone);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Номер телефона"
        type="tel"
        placeholder="+7 (999) 999-99-99"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        error={error}
        disabled={loading}
      />
      <Button type="submit" loading={loading} className="w-full">
        Получить код
      </Button>
    </form>
  );
};
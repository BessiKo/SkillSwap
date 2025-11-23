import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

interface CodeFormProps {
  phone: string;
  onVerify: (code: string) => Promise<void>;
  loading?: boolean;
  onResendCode: () => void;
}

export const CodeForm: React.FC<CodeFormProps> = ({
  phone,
  onVerify,
  loading = false,
  onResendCode,
}) => {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!code.trim() || code.length !== 6) {
      setError('Введите 6-значный код');
      return;
    }

    try {
      await onVerify(code);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <p className="text-sm text-gray-600">
        Код отправлен на {phone}
      </p>
      
      <Input
        label="Код подтверждения"
        type="text"
        placeholder="123456"
        maxLength={6}
        value={code}
        onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
        error={error}
        disabled={loading}
      />
      
      <Button type="submit" loading={loading} className="w-full">
        Войти
      </Button>
      
      <Button
        type="button"
        variant="outline"
        className="w-full"
        onClick={onResendCode}
        disabled={loading}
      >
        Отправить код повторно
      </Button>
    </form>
  );
};
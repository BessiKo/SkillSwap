import { useState } from 'react';

interface Props {
  onSubmit: (phone: string) => Promise<void>;
  isLoading: boolean;
  error?: string;
}

export function PhoneInput({ onSubmit, isLoading, error }: Props) {
  const [phone, setPhone] = useState('');

  const formatPhone = (value: string) => {
    const digits = value.replace(/\D/g, '');
    if (digits.length <= 1) return '+7';
    if (digits.length <= 4) return `+7 (${digits.slice(1)}`;
    if (digits.length <= 7) return `+7 (${digits.slice(1, 4)}) ${digits.slice(4)}`;
    if (digits.length <= 9) return `+7 (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7)}`;
    return `+7 (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7, 9)}-${digits.slice(9, 11)}`;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhone(e.target.value);
    setPhone(formatted);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanPhone = '+7' + phone.replace(/\D/g, '').slice(1);
    onSubmit(cleanPhone);
  };

  const isValid = phone.replace(/\D/g, '').length === 11;

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Скилл Свап</h1>
        <p className="text-gray-600 mt-2">Войдите для обмена знаниями</p>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Номер телефона
        </label>
        <input
          type="tel"
          value={phone}
          onChange={handleChange}
          placeholder="+7 (___) ___-__-__"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-lg"
          autoFocus
        />
        
        {error && (
          <p className="mt-2 text-sm text-red-600">{error}</p>
        )}

        <button
          onClick={handleSubmit}
          disabled={!isValid || isLoading}
          className="w-full mt-4 py-3 px-4 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Отправка...
            </span>
          ) : 'Получить код'}
        </button>
      </div>
    </div>
  );
}
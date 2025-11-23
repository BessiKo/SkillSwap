import React, { useState } from 'react';
import { PhoneForm } from '../components/auth/PhoneForm';
import { CodeForm } from '../components/auth/CodeForm';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/auth';

export const LoginPage: React.FC = () => {
  const [step, setStep] = useState<'phone' | 'code'>('phone');
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handlePhoneSubmit = async (phoneNumber: string) => {
    setLoading(true);
    try {
      await authService.requestCode(phoneNumber);
      setPhone(phoneNumber);
      setStep('code');
    } catch (error) {
      console.error('Failed to request code:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleCodeVerify = async (code: string) => {
    setLoading(true);
    try {
      const result = await login(phone, code);
      if (!result.success) {
        throw new Error(result.error);
      }
      // Перенаправление произойдет автоматически через роутинг
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    try {
      await authService.requestCode(phone);
    } catch (error) {
      console.error('Failed to resend code:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            SkillSwap
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Обмен знаниями в университете
          </p>
        </div>
        
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {step === 'phone' ? (
            <PhoneForm onCodeSent={handlePhoneSubmit} loading={loading} />
          ) : (
            <CodeForm
              phone={phone}
              onVerify={handleCodeVerify}
              loading={loading}
              onResendCode={handleResendCode}
            />
          )}
        </div>
      </div>
    </div>
  );
};
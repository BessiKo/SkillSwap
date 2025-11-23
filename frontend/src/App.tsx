import { useState, useEffect, useContext, createContext, useMemo, useCallback } from 'react';

type UserRole = 'student' | 'admin';

interface Badge {
  id: number;
  name: string;
  type: string; 
  description: string;
  icon: string;
}

interface UserProfile {
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  bio: string;
  university: string;
  faculty: string;
  year: number | null;
  rating: number;
  total_ratings: number;
  exchanges_completed: number;
  reviews_received: number;
}

interface User {
  id: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  profile: UserProfile | null;
  badges: Badge[];
}

interface TokenResponse {
  access_token: string;
  expires_in: number;
  is_new_user: boolean;
}

interface CodeRequestResponse {
    message: string;
    expires_in: number;
    debugCode?: string; 
    success: boolean; 
    error?: string;   
}

interface ProfileUpdateData {
  first_name?: string;
  last_name?: string;
  bio?: string;
  university?: string;
  faculty?: string;
  year?: number | null;
}

interface CodeInputProps {
    phone: string;
    onCodeVerified: (phone: string, isNewUser: boolean) => void;
    onCancel: () => void;
    onBack: () => void;
    codeRequestDebug?: string;
}

interface PhoneRequestProps {
    onCodeRequested: (phone: string, debugCode?: string) => void;
    isLoading: boolean;
    error: string | null;
}


const API_URL = 'http://localhost:8000/api/v1';

// Базовый клиент для Fetch API
async function apiClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };

  const config: RequestInit = {
    ...options,
    headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, config);

  if (response.status === 401 && endpoint !== '/auth/refresh') {
    try {
      await refreshToken();
      const newToken = localStorage.getItem('accessToken');
      if (newToken) {
        config.headers = {
          ...headers,
          'Authorization': `Bearer ${newToken}`
        };
        const retryResponse = await fetch(`${API_URL}${endpoint}`, config);
        if (retryResponse.ok) return await retryResponse.json() as T;
      }
    } catch (refreshError) {
      console.error('Token refresh failed, logging out:', refreshError);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
      window.location.reload();
    }
  }

  if (!response.ok) {
    let errorDetail = await response.text();
    try {
      const jsonError = JSON.parse(errorDetail);
      errorDetail = jsonError.detail || errorDetail;
    } catch (e) {
    }
    throw new Error(errorDetail || response.statusText);
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.indexOf("application/json") !== -1) {
    return await response.json() as T;
  }
  
  return null as T;
}

async function refreshToken(): Promise<void> {
    const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
        throw new Error('Refresh token failed');
    }

    const data: TokenResponse = await response.json();
    localStorage.setItem('accessToken', data.access_token);
}

const api = {
  requestCode: (phone: string): Promise<CodeRequestResponse> =>
    apiClient<CodeRequestResponse>('/auth/request_code', {
      method: 'POST',
      body: JSON.stringify({ phone }),
    }),

  verifyCode: (phone: string, code: string): Promise<TokenResponse> =>
    apiClient<TokenResponse>('/auth/verify_code', {
      method: 'POST',
      body: JSON.stringify({ phone, code }),
    }),

  logout: () => apiClient('/auth/logout', { method: 'POST' }),
  fetchMe: (): Promise<User> => apiClient<User>('/users/me'),
  
  updateProfile: (data: ProfileUpdateData): Promise<User> =>
    apiClient<User>('/users/me/profile', {
        method: 'PATCH',
        body: JSON.stringify(data),
    }),
};


interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  login: (phone: string, code: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (profile: ProfileUpdateData) => Promise<void>;
  requestAuthCode: (phone: string) => Promise<CodeRequestResponse>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      try {
        const userData = await api.fetchMe();
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error("Failed to fetch user or token expired:", error);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('user');
        setIsAuthenticated(false);
      }
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const requestAuthCode = async (phone: string) => {
    return api.requestCode(phone);
  };

  const login = async (phone: string, code: string) => {
    setIsLoading(true);
    try {
      const response = await api.verifyCode(phone, code);
      localStorage.setItem('accessToken', response.access_token);
      await loadUser();
      return;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await api.logout();
    } catch (e) {
      console.error("Logout failed on server, proceeding with client logout:", e);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
    }
  };
  
  const updateUser = async (profileData: ProfileUpdateData) => {
    try {
        const updatedUser = await api.updateProfile(profileData);
        setUser(updatedUser);
    } catch (error) {
        console.error("Failed to update profile:", error);
        throw error;
    }
  }


  const value = useMemo(() => ({
    isAuthenticated,
    isLoading,
    user,
    login,
    logout,
    updateUser,
    requestAuthCode,
  }), [isAuthenticated, isLoading, user]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

const APP_TITLE = "Skill Swap";
const APP_SLOGAN = "Платформа для обмена знаниями";
const LOGO_SRC = "LOGO.PNG"; 

function LoadingScreen() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
            <svg className="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="mt-4 text-gray-600">Загрузка...</p>
        </div>
    );
}

const AuthHeader = () => (
    <div className="text-center p-6 bg-indigo-50 rounded-t-xl">
        <img 
            src={LOGO_SRC} 
            alt="Логотип Skill Swap" 
            className="h-20 w-auto mx-auto mb-2" 
        />
        <h1 className="text-2xl font-extrabold text-indigo-700">
            {APP_TITLE}
        </h1>
        <p className="text-sm text-gray-600 mt-1">{APP_SLOGAN}</p>
    </div>
);

function RequestCodeForm({ onCodeRequested, isLoading, error }: PhoneRequestProps) {
    const [phone, setPhone] = useState('');
    const [localError, setLocalError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLocalError(null);
        if (!/^\+7\d{10}$/.test(phone)) {
            setLocalError('Неверный формат телефона. Используйте формат: +7xxxxxxxxxx');
            return;
        }

        try {
            const response = await requestAuthCode(phone);
            onCodeRequested(phone, response.debugCode);
        } catch (err) {
            setLocalError(err instanceof Error ? err.message : 'Ошибка запроса кода');
        }
    };

    const { requestAuthCode } = useAuth();


    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            <h2 className="text-2xl font-semibold text-gray-800">Вход / Регистрация</h2>
            <p className="text-gray-600">Введите свой номер телефона для получения SMS-кода.</p>
            
            <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">Номер телефона</label>
                <input
                    id="phone"
                    type="tel"
                    value={phone}
                    onChange={(e) => {
                        setPhone(e.target.value);
                        setLocalError(null);
                    }}
                    placeholder="+79001234567"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
                    disabled={isLoading}
                />
            </div>
            
            {(localError || error) && (
                <div className="text-sm p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                    {localError || error}
                </div>
            )}

            <button
                type="submit"
                className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50"
                disabled={isLoading || !phone}
            >
                {isLoading ? (
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                ) : (
                    'Получить код'
                )}
            </button>
        </form>
    );
}

function CodeInput({ phone, onCodeVerified, onCancel, onBack, codeRequestDebug }: CodeInputProps) {
    const [code, setCode] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { login } = useAuth();
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        if (!/^\d{6}$/.test(code)) {
            setError('Код должен состоять из 6 цифр.');
            return;
        }

        setIsLoading(true);
        try {
            await login(phone, code);
            onCodeVerified(phone, false);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Ошибка верификации кода');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            <button
                type="button"
                onClick={onBack}
                className="text-sm text-indigo-600 hover:text-indigo-800 transition-colors flex items-center mb-4"
            >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                Назад к телефону
            </button>
            
            <h2 className="text-2xl font-semibold text-gray-800">Введите код</h2>
            <p className="text-gray-600">
                Код отправлен на номер <span className="font-medium text-indigo-600">{phone}</span>.
            </p>
            
            {codeRequestDebug && (
                <div className="text-sm p-3 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded-lg">
                    [DEBUG] Код: <span className="font-mono font-bold">{codeRequestDebug}</span>
                </div>
            )}
            
            <div>
                <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1">Код подтверждения (6 цифр)</label>
                <input
                    id="code"
                    type="text"
                    inputMode="numeric"
                    pattern="\d{6}"
                    value={code}
                    onChange={(e) => {
                        const numericValue = e.target.value.replace(/\D/g, '').slice(0, 6);
                        setCode(numericValue);
                        setError(null);
                    }}
                    placeholder="123456"
                    className="w-full px-4 py-2 text-center text-lg border-2 border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 tracking-widest font-mono"
                    disabled={isLoading}
                />
            </div>
            
            {error && (
                <div className="text-sm p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                    {error}
                </div>
            )}

            <button
                type="submit"
                className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50"
                disabled={isLoading || code.length !== 6}
            >
                {isLoading ? (
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                ) : (
                    'Войти'
                )}
            </button>

            <button
                type="button"
                onClick={onCancel}
                className="w-full py-2 text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
                Отмена
            </button>
        </form>
    );
}

function AuthScreen() {
    const [step, setStep] = useState<'request' | 'verify'>('request');
    const [phone, setPhone] = useState('');
    const [debugCode, setDebugCode] = useState<string | undefined>(undefined);
    const [requestError, setRequestError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleCodeRequested = (requestedPhone: string, debug: string | undefined) => {
        setPhone(requestedPhone);
        setDebugCode(debug);
        setRequestError(null);
        setStep('verify');
        setIsLoading(false);
    };
    
    const handleCodeVerificationStart = () => {
        setIsLoading(true);
        setRequestError(null);
    }

    const handleCodeVerified = (verifiedPhone: string, isNewUser: boolean) => {
        console.log(`User ${verifiedPhone} logged in. New user: ${isNewUser}`);
    };

    const handleCancel = () => {
        setStep('request');
        setPhone('');
        setDebugCode(undefined);
        setRequestError(null);
        setIsLoading(false);
    };
    
    const handleBack = () => {
        setStep('request');
        setDebugCode(undefined);
        setRequestError(null);
    }

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
            <div className="w-full max-w-md bg-white rounded-xl shadow-2xl"> 
                
                <AuthHeader />
                <div className="p-8">
                    
                    {step === 'request' && (
                        <RequestCodeForm 
                            onCodeRequested={handleCodeRequested} 
                            isLoading={isLoading} 
                            error={requestError}
                        />
                    )}
                    
                    {step === 'verify' && (
                        <CodeInput
                            phone={phone}
                            onCodeVerified={handleCodeVerified}
                            onCancel={handleCancel}
                            onBack={handleBack}
                            codeRequestDebug={debugCode}
                        />
                    )}
                </div>
            </div>
        </div>
    );
}

const BadgeItem: React.FC<{ badge: Badge }> = ({ badge }) => (
    <div className="flex items-center space-x-2 bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-xs font-medium shadow-sm">
        <span className="text-sm">{badge.icon}</span>
        <span>{badge.name}</span>
    </div>
);

const RatingDisplay: React.FC<{ rating: number, total: number }> = ({ rating, total }) => {
    const starCount = Math.round(rating);
    const stars = Array(5).fill(0).map((_, i) => (
        <svg key={i} className={`w-4 h-4 ${i < starCount ? 'text-yellow-400' : 'text-gray-300'} inline`} fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.968a1 1 0 00.95.691h4.17c.97 0 1.364 1.25.588 1.81l-3.375 2.454a1 1 0 00-.364 1.118l1.286 3.968c.3.921-.755 1.688-1.539 1.118l-3.375-2.454a1 1 0 00-1.175 0l-3.375 2.454c-.784.57-1.838-.197-1.539-1.118l1.286-3.968a1 1 0 00-.364-1.118L2.05 9.396c-.776-.56-.381-1.81.588-1.81h4.17a1 1 0 00.95-.691l1.286-3.968z" />
        </svg>
    ));

    return (
        <div className="flex items-center space-x-2">
            <div>{stars}</div>
            <span className="text-sm font-medium text-gray-700">{rating.toFixed(1)}</span>
            <span className="text-xs text-gray-500">({total} оценок)</span>
        </div>
    );
};

const ProfileView: React.FC<{ user: User, onEdit: () => void, isOwnProfile: boolean }> = ({ user, onEdit, isOwnProfile }) => {
    
    const profile = user.profile || {
        first_name: 'Пользователь',
        last_name: 'SkillSwap',
        avatar_url: null,
        bio: 'Профиль еще не заполнен.',
        university: '',
        faculty: '',
        year: null,
        rating: 0,
        total_ratings: 0,
        exchanges_completed: 0,
        reviews_received: 0,
    };
    
    const isProfileComplete = !!user.profile?.first_name;

    if (!isProfileComplete) {
        return (
            <div className="bg-white p-6 rounded-xl shadow-lg text-center space-y-4">
                <h2 className="text-2xl font-bold text-red-500">Незавершенный профиль</h2>
                <p className="text-gray-600">
                    Добро пожаловать! Чтобы начать использовать платформу, пожалуйста, заполните свою основную информацию.
                </p>
                <button
                    onClick={onEdit}
                    className="mt-4 px-6 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-md"
                >
                    Заполнить профиль
                </button>
            </div>
        );
    }
    
    const avatarUrl = profile.avatar_url ? `${API_URL}${profile.avatar_url}` : `https://placehold.co/128x128/6366f1/ffffff?text=${profile.first_name[0]}`;

    return (
        <div className="bg-white p-6 rounded-xl shadow-xl space-y-6">
            <div className="flex flex-col sm:flex-row items-center sm:items-start space-y-4 sm:space-y-0 sm:space-x-6">
                <img 
                    src={avatarUrl} 
                    alt="Аватар" 
                    className="w-32 h-32 object-cover rounded-full border-4 border-indigo-200 shadow-md"
                    onError={(e) => {
                        (e.target as HTMLImageElement).onerror = null; 
                        (e.target as HTMLImageElement).src = `https://placehold.co/128x128/6366f1/ffffff?text=${profile.first_name[0]}`;
                    }}
                />
                
                <div className="flex-1 text-center sm:text-left">
                    <h2 className="text-3xl font-extrabold text-gray-800">
                        {profile.first_name} {profile.last_name}
                    </h2>
                    <p className="text-lg text-indigo-600 mt-1">{profile.faculty}{profile.year && `, ${profile.year} курс`}</p>
                    <p className="text-sm text-gray-500">{profile.university}</p>
                    
                    <div className="mt-3">
                        <RatingDisplay rating={profile.rating} total={profile.total_ratings} />
                    </div>
                </div>
                
                {isOwnProfile && (
                    <button
                        onClick={onEdit}
                        className="self-start sm:self-auto px-4 py-2 text-sm bg-indigo-50 text-indigo-600 font-medium rounded-lg hover:bg-indigo-100 transition-colors shadow-sm"
                    >
                        Редактировать
                    </button>
                )}
            </div>

            <hr className="border-gray-200" />

            <div className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-800">О себе</h3>
                <p className="text-gray-600 whitespace-pre-wrap">{profile.bio || "Пользователь пока не заполнил информацию о себе."}</p>
            </div>
            
            <div className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-800">Достижения</h3>
                <div className="flex flex-wrap gap-2">
                    {user.badges.length > 0 ? (
                        user.badges.map(badge => <BadgeItem key={badge.id} badge={badge} />)
                    ) : (
                        <p className="text-gray-500 text-sm">Нет баджей. Начните обмениваться знаниями, чтобы их получить!</p>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
                <div className="text-center p-3 bg-gray-50 rounded-lg shadow-inner">
                    <p className="text-2xl font-bold text-indigo-600">{profile.exchanges_completed}</p>
                    <p className="text-sm text-gray-500">Обменов завершено</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg shadow-inner">
                    <p className="text-2xl font-bold text-indigo-600">{profile.reviews_received}</p>
                    <p className="text-sm text-gray-500">Отзывов получено</p>
                </div>
            </div>
            
            <p className="text-xs text-gray-400 pt-4 border-t border-gray-100">
                Телефон: {user.phone} | ID: {user.id}
            </p>
        </div>
    );
};

const ProfileEdit: React.FC<{ user: User, onClose: () => void }> = ({ user, onClose }) => {
    const { updateUser } = useAuth();
    const initialProfile = user.profile || {
        first_name: '',
        last_name: '',
        bio: '',
        university: '',
        faculty: '',
        year: null,
    } as Partial<UserProfile>;

    const [formData, setFormData] = useState<ProfileUpdateData>({
        first_name: initialProfile.first_name || '',
        last_name: initialProfile.last_name || '',
        bio: initialProfile.bio || '',
        university: initialProfile.university || '',
        faculty: initialProfile.faculty || '',
        year: initialProfile.year || null,
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'number' ? (value ? parseInt(value) : null) : value,
        }));
        setError(null);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);
        
        try {
            const dataToSend: ProfileUpdateData = Object.fromEntries(
                Object.entries(formData).filter(([_, v]) => v !== null && v !== '')
            );

            await updateUser(dataToSend);
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Не удалось обновить профиль');
        } finally {
            setIsLoading(false);
        }
    };
    
    return (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-gray-900 bg-opacity-75 flex items-center justify-center p-4" onClick={onClose}>
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg relative" onClick={(e) => e.stopPropagation()}>
                <button 
                    onClick={onClose} 
                    className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
                    aria-label="Закрыть"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>

                <div className="p-8 space-y-6">
                    <h2 className="text-2xl font-bold text-gray-800">Редактирование профиля</h2>
                    
                    {error && (
                        <div className="text-sm p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                            {error}
                        </div>
                    )}
                    
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {/* Имя */}
                            <div>
                                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                                <input
                                    id="first_name"
                                    name="first_name"
                                    type="text"
                                    value={formData.first_name || ''}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                    required
                                />
                            </div>
                            {/* Фамилия */}
                            <div>
                                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
                                <input
                                    id="last_name"
                                    name="last_name"
                                    type="text"
                                    value={formData.last_name || ''}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                    required
                                />
                            </div>
                        </div>

                        {/* Университет */}
                        <div>
                            <label htmlFor="university" className="block text-sm font-medium text-gray-700 mb-1">Университет</label>
                            <input
                                id="university"
                                name="university"
                                type="text"
                                value={formData.university || ''}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                            />
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                            {/* Факультет */}
                            <div>
                                <label htmlFor="faculty" className="block text-sm font-medium text-gray-700 mb-1">Факультет</label>
                                <input
                                    id="faculty"
                                    name="faculty"
                                    type="text"
                                    value={formData.faculty || ''}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>
                            {/* Курс */}
                            <div>
                                <label htmlFor="year" className="block text-sm font-medium text-gray-700 mb-1">Курс (Год обучения)</label>
                                <input
                                    id="year"
                                    name="year"
                                    type="number"
                                    min="1"
                                    max="6"
                                    value={formData.year || ''}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                    placeholder="Например, 3"
                                />
                            </div>
                        </div>

                        {/* Биография */}
                        <div>
                            <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-1">О себе / Биография</label>
                            <textarea
                                id="bio"
                                name="bio"
                                rows={4}
                                value={formData.bio || ''}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                placeholder="Расскажите о своих навыках и интересах..."
                            />
                        </div>

                        <div className="flex justify-end space-x-3 pt-4">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                                disabled={isLoading}
                            >
                                Отмена
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 flex items-center justify-center text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors shadow-md disabled:opacity-50"
                                disabled={isLoading || !formData.first_name || !formData.last_name}
                            >
                                {isLoading ? (
                                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                ) : (
                                    'Сохранить'
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};


function MainApp() {
  const { user, logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  
  if (!user) {
    return <AuthScreen />;
  }

  const LOGO_SRC = "LOGO.PNG";

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Шапка */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex justify-between items-center">

        <div className="flex items-center gap-2">
            <img 
                src={LOGO_SRC} 
                alt="Логотип Skill Swap" 
                className="h-6 w-auto rounded-md" 
            />
            <h1 className="text-xl font-bold text-indigo-600">{APP_TITLE}</h1>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600 hidden sm:inline">{user.phone}</span>
            <button
              onClick={logout}
              className="px-3 py-1 bg-gray-100 text-sm text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Выйти
            </button>
          </div>
        </div>
      </header>

      {/* Основное содержимое */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <ProfileView 
          user={user} 
          onEdit={() => setIsEditing(true)} 
          isOwnProfile
        />
      </main>

      {/* Модальное окно редактирования */}
      {isEditing && (
        <ProfileEdit 
          user={user} 
          onClose={() => setIsEditing(false)} 
        />
      )}
    </div>
  );
}

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <AuthScreen />;
  }

  return <MainApp />;
}

export default function App() {
  return (
    <AuthProvider>
        <AppContent />
    </AuthProvider>
  )
}
// API 基础配置
const API_BASE_URL = 'http://localhost:8000';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  avatar?: string;
}

// 获取存储的 token
export function getStoredToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
}

// 存储 token
export function setStoredToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', token);
  }
}

// 清除 token
export function clearStoredToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
  }
}

// 登录 API
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '登录失败');
  }

  const data = await response.json() as TokenResponse;
  setStoredToken(data.access_token);
  return data;
}

// 获取当前用户信息 API
export async function getCurrentUser(): Promise<User> {
  const token = getStoredToken();

  if (!token) {
    throw new Error('未登录');
  }

  const response = await fetch(`${API_BASE_URL}/api/users/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      clearStoredToken();
    }
    const error = await response.json();
    throw new Error(error.detail || '获取用户信息失败');
  }

  return response.json() as Promise<User>;
}

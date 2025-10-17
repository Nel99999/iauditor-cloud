import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// Types
interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  organization_id?: string;
  [key: string]: any;
}

interface Permission {
  id: string;
  name: string;
  code: string;
  description?: string;
  [key: string]: any;
}

interface Role {
  id: string;
  name: string;
  code: string;
  level?: number;
  [key: string]: any;
}

interface AuthResponse {
  success: boolean;
  error?: string;
  user?: User;
}

interface AuthContextType {
  user: User | null;
  userPermissions: Permission[];
  userRole: Role | null;
  loading: boolean;
  register: (email: string, password: string, name: string, organizationName: string) => Promise<AuthResponse>;
  login: (email: string, password: string) => Promise<AuthResponse>;
  loginWithGoogle: () => void;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userPermissions, setUserPermissions] = useState<Permission[]>([]);
  const [userRole, setUserRole] = useState<Role | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Fetch user permissions based on their role
  const loadUserPermissions = async (userRole: string, _userId: string): Promise<void> => {
    try {
      // Get all roles to find the user's role ID
      const rolesResponse = await axios.get<Role[]>(`${API}/roles`);
      const userRoleData = rolesResponse.data.find(r => r.code === userRole);
      
      if (userRoleData) {
        // Get permissions for this role
        const permResponse = await axios.get<any[]>(`${API}/roles/${userRoleData.id}/permissions`);
        
        // Get permission details
        const permissionsResponse = await axios.get<Permission[]>(`${API}/permissions`);
        const allPermissions = permissionsResponse.data;
        
        // Map role_permissions to actual permission objects
        const userPerms = permResponse.data.map(rp => {
          return allPermissions.find(p => p.id === rp.permission_id);
        }).filter((p): p is Permission => Boolean(p));
        
        setUserPermissions(userPerms);
        setUserRole(userRoleData);
        
        console.log(`✅ Loaded ${userPerms.length} permissions for role: ${userRole}`);
      }
    } catch (error) {
      console.error('Failed to load permissions:', error);
      setUserPermissions([]);
    }
  };

  // Check for existing session on mount
  useEffect(() => {
    const initAuth = async () => {
      // Check for session_id in URL fragment (Google OAuth callback)
      const hash = window.location.hash;
      const sessionIdMatch = hash.match(/session_id=([^&]+)/);
      
      if (sessionIdMatch) {
        const sessionId = sessionIdMatch[1];
        await handleGoogleCallback(sessionId);
        // Clean URL
        window.history.replaceState(null, '', window.location.pathname);
        return;
      }

      // Check for existing token
      if (token) {
        try {
          const response = await axios.get<User>(`${API}/auth/me`);
          const userData = response.data;
          setUser(userData);
          
          // Load permissions for user's role
          if (userData.role) {
            await loadUserPermissions(userData.role, userData.id);
          }
        } catch (error) {
          console.error('Failed to fetch user:', error);
          localStorage.removeItem('access_token');
          setToken(null);
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  const handleGoogleCallback = async (sessionId: string): Promise<void> => {
    setLoading(true);
    try {
      const response = await axios.post<{ user: User }>(`${API}/auth/google/callback`, null, {
        params: { session_id: sessionId },
        withCredentials: true,
      });
      
      const userData = response.data.user;
      setUser(userData);
      
      // Load permissions
      if (userData.role) {
        await loadUserPermissions(userData.role, userData.id);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Google OAuth error:', error);
      setLoading(false);
    }
  };

  const register = async (
    email: string,
    password: string,
    name: string,
    organizationName: string
  ): Promise<AuthResponse> => {
    try {
      const response = await axios.post<{ access_token: string; user: User }>(`${API}/auth/register`, {
        email,
        password,
        name,
        organization_name: organizationName,
      });
      
      const { access_token, user: userData } = response.data;
      
      // Check if user is pending approval (no token will be provided)
      if (userData.approval_status === 'pending' || !access_token) {
        // Don't set token or user in context - user needs approval first
        return { 
          success: true,
          user: userData  // Pass user data so RegisterPage can check approval_status
        };
      }
      
      // Normal flow (user is approved)
      localStorage.setItem('access_token', access_token);
      setToken(access_token);
      setUser(userData);
      
      // Load permissions
      if (userData.role) {
        await loadUserPermissions(userData.role, userData.id);
      }
      
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  };

  const login = async (email: string, password: string): Promise<AuthResponse> => {
    try {
      const response = await axios.post<{ access_token: string; user: User }>(`${API}/auth/login`, {
        email,
        password,
      });
      
      const { access_token, user: userData } = response.data;
      localStorage.setItem('access_token', access_token);
      setToken(access_token);
      setUser(userData);
      
      // Load permissions
      if (userData.role) {
        await loadUserPermissions(userData.role, userData.id);
      }
      
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const loginWithGoogle = (): void => {
    const redirectUrl = `${window.location.origin}/dashboard`;
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const logout = async (): Promise<void> => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      setToken(null);
      setUser(null);
      setUserPermissions([]);
      setUserRole(null);
    }
  };

  const value: AuthContextType = {
    user,
    userPermissions,
    userRole,
    loading,
    register,
    login,
    loginWithGoogle,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

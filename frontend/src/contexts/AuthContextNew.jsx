import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [userPermissions, setUserPermissions] = useState([]);
  const [userRole, setUserRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('access_token'));

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Fetch user permissions based on their role
  const loadUserPermissions = async (userRole, userId) => {
    try {
      // Get all roles to find the user's role ID
      const rolesResponse = await axios.get(`${API}/roles`);
      const userRoleData = rolesResponse.data.find(r => r.code === userRole);
      
      if (userRoleData) {
        // Get permissions for this role
        const permResponse = await axios.get(`${API}/roles/${userRoleData.id}/permissions`);
        
        // Get permission details
        const permissionsResponse = await axios.get(`${API}/permissions`);
        const allPermissions = permissionsResponse.data;
        
        // Map role_permissions to actual permission objects
        const userPerms = permResponse.data.map(rp => {
          return allPermissions.find(p => p.id === rp.permission_id);
        }).filter(Boolean);
        
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
          const response = await axios.get(`${API}/auth/me`);
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

  const handleGoogleCallback = async (sessionId) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/google/callback`, null, {
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

  const register = async (email, password, name, organizationName) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email,
        password,
        name,
        organization_name: organizationName,
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
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
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
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const loginWithGoogle = () => {
    const redirectUrl = `${window.location.origin}/dashboard`;
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const logout = async () => {
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

  const value = {
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

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

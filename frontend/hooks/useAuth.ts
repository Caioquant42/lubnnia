/**
 * Authentication Hook
 * Manages user authentication state, login, logout, and session persistence
 * Uses localStorage for session management and provides authentication utilities
 */
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export type User = {
  id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';
  user_metadata?: {
    avatar_url?: string;
    role?: string;
    [key: string]: any;
  };
  // Add other user properties as needed
};

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  useEffect(() => {
    // Check if user is logged in by fetching from localStorage or a cookie
    const checkAuth = () => {
      try {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          // Parse stored user and ensure it has the expected structure
          const parsedUser = JSON.parse(storedUser);
          
          // Make sure user_metadata exists to prevent TypeScript errors
          if (!parsedUser.user_metadata) {
            parsedUser.user_metadata = {
              avatar_url: '',
              role: parsedUser.role || 'user'
            };
          }
          
          setUser(parsedUser);
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);
  const login = async (email: string, password: string) => {
    try {
      // Implementation of login logic
      // This would typically involve an API call
      
      // For demo purposes, include user_metadata like Supabase would:
      const mockUser = {
        id: '1',
        name: 'Demo User',
        email,
        role: 'user' as const,
        user_metadata: {
          avatar_url: '',  // Default empty avatar URL
          role: 'user',
        }
      };
      
      localStorage.setItem('user', JSON.stringify(mockUser));
      setUser(mockUser);
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('user');
    setUser(null);
    router.push('/auth/login');
  };

  return {
    user,
    login,
    logout,
    loading,
    isAuthenticated: !!user,
  };
}

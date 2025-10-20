/**
 * Admin Role Check Hook
 * Utility hook to check if the current user has admin privileges
 * @returns {Object} Object containing isAdmin boolean
 */
import { useAuth } from './useAuth';

export function useIsAdmin() {
  const { user } = useAuth();
  
  return {
    isAdmin: user?.role === 'admin',
  };
}

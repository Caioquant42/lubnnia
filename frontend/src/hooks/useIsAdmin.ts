import { useAuth } from './useAuth';

export function useIsAdmin() {
  const { user } = useAuth();
  
  return {
    isAdmin: user?.role === 'admin',
  };
}

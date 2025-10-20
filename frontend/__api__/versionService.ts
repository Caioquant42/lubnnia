/**
 * Version Service
 * Handles version checking for cache invalidation
 */
import apiService from './apiService';

export interface VersionInfo {
  version: string;
  build_time: string;
  git_commit: string;
  timestamp: number;
  cache_bust: string;
}

export const checkVersion = async (): Promise<VersionInfo> => {
  try {
    const response = await apiService.get('/version');
    return response.data;
  } catch (error) {
    console.error('Version check failed:', error);
    throw error;
  }
};

export const shouldUpdateCache = (currentVersion: string, newVersion: string): boolean => {
  return currentVersion !== newVersion;
};

export const getCurrentVersion = (): string => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('app_version') || '1.0.0';
  }
  return '1.0.0';
};

export const setCurrentVersion = (version: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('app_version', version);
  }
};

export const clearCache = (): void => {
  if (typeof window !== 'undefined') {
    // Clear localStorage
    localStorage.clear();
    
    // Clear any service worker caches
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => {
          caches.delete(name);
        });
      });
    }
    
    // Reload the page
    window.location.reload();
  }
};

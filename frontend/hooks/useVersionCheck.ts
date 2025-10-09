/**
 * Version Check Hook
 * Monitors for application updates and handles cache invalidation
 */
import { useEffect, useState } from 'react';
import { checkVersion, shouldUpdateCache, getCurrentVersion, setCurrentVersion, clearCache } from '../__api__/versionService';

export const useVersionCheck = (checkInterval: number = 5 * 60 * 1000) => { // Default: 5 minutes
  const [needsUpdate, setNeedsUpdate] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [currentVersion, setCurrentVersionState] = useState<string>('1.0.0');

  useEffect(() => {
    const checkForUpdates = async () => {
      setIsChecking(true);
      try {
        const versionInfo = await checkVersion();
        const storedVersion = getCurrentVersion();
        
        setCurrentVersionState(versionInfo.version);
        
        if (shouldUpdateCache(storedVersion, versionInfo.version)) {
          setNeedsUpdate(true);
          console.log(`Update available: ${storedVersion} -> ${versionInfo.version}`);
        }
      } catch (error) {
        console.error('Version check failed:', error);
      } finally {
        setIsChecking(false);
      }
    };

    // Initial check
    checkForUpdates();

    // Set up interval for periodic checks
    const interval = setInterval(checkForUpdates, checkInterval);

    return () => clearInterval(interval);
  }, [checkInterval]);

  const forceUpdate = () => {
    console.log('Forcing cache update...');
    clearCache();
  };

  const dismissUpdate = () => {
    // Update the stored version to current version
    setCurrentVersion(currentVersion);
    setNeedsUpdate(false);
  };

  return { 
    needsUpdate, 
    isChecking, 
    currentVersion, 
    forceUpdate, 
    dismissUpdate 
  };
};

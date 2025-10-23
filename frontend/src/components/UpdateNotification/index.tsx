/**
 * Update Notification Component
 * Shows a notification when a new version is available
 */
'use client';

import { RefreshCw, X } from 'lucide-react';
import React from 'react';

import { useVersionCheck } from '../../hooks/useVersionCheck';

import { Alert, AlertDescription } from '../ui/alert';
import { Button } from '../ui/button';

export const UpdateNotification: React.FC = () => {
  const {
    needsUpdate,
    isChecking,
    currentVersion,
    forceUpdate,
    dismissUpdate,
  } = useVersionCheck();

  if (!needsUpdate) {
    return null;
  }

  return (
    <div className='fixed top-4 right-4 z-50 max-w-md'>
      <Alert className='border-orange-200 bg-orange-50'>
        <RefreshCw className='h-4 w-4' />
        <AlertDescription className='flex items-center justify-between'>
          <div>
            <p className='font-medium text-orange-800'>
              Nova versão disponível!
            </p>
            <p className='text-sm text-orange-700'>
              Versão {currentVersion} está disponível. Atualize para ver as
              últimas mudanças.
            </p>
          </div>
          <div className='flex gap-2 ml-4'>
            <Button
              size='sm'
              onClick={forceUpdate}
              disabled={isChecking}
              className='bg-orange-600 hover:bg-orange-700'
            >
              {isChecking ? (
                <RefreshCw className='h-4 w-4 animate-spin' />
              ) : (
                'Atualizar'
              )}
            </Button>
            <Button
              size='sm'
              variant='outline'
              onClick={dismissUpdate}
              className='border-orange-300 text-orange-700 hover:bg-orange-100'
            >
              <X className='h-4 w-4' />
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    </div>
  );
};

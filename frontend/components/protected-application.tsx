'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { hasApplicationAccess, ApplicationId } from '@/lib/permissions';

interface ProtectedApplicationProps {
  applicationId: string;
  fallback?: React.ReactNode;
  children: React.ReactNode;
  redirectTo?: string;
}

/**
 * Component to protect content based on user's tier access
 * If the user doesn't have access to the application, either shows 
 * the fallback content or redirects to the specified path
 */
export function ProtectedApplication({
  applicationId,
  fallback,
  children,
  redirectTo
}: ProtectedApplicationProps) {
  const [hasAccess, setHasAccess] = useState<boolean | null>(null);
  const router = useRouter();
  useEffect(() => {
    const checkAccess = async () => {
      // Cast the applicationId string to ApplicationId type
      const access = await hasApplicationAccess(applicationId as ApplicationId);
      setHasAccess(access);

      if (!access && redirectTo) {
        router.push(redirectTo);
      }
    };

    checkAccess();
  }, [applicationId, redirectTo, router]);

  // Initial loading state
  if (hasAccess === null) {
    return <div className="p-8 flex justify-center">Carregando...</div>;
  }

  // User doesn't have access and we're showing fallback
  if (!hasAccess && !redirectTo) {
    return fallback || (
      <div className="p-8 flex flex-col items-center justify-center space-y-4">
        <h3 className="text-xl font-medium">Acesso Limitado</h3>
        <p className="text-muted-foreground text-center max-w-md">
          Este recurso está disponível apenas para assinantes de planos superiores.
          Atualize seu plano para acessar este conteúdo.
        </p>
        <a href="/pricing" className="text-finance-secondary-500 underline-offset-4 hover:underline">
          Ver planos disponíveis
        </a>
      </div>
    );
  }

  // User has access, render children
  return <>{children}</>;
}

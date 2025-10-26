'use client';

import { ArrowRight, CheckCircle, Mail, RefreshCw } from 'lucide-react';
import Image from 'next/image';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

// import { supabase } from '@/lib/supabase-old';
import { createClientBrowser } from '@/lib/supabaseClient';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

import noBackground from '../../../../public/logoFiles/web/png/colorLogoWithoutBackground.png';

export default function EmailConfirmedPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resendingEmail, setResendingEmail] = useState(false);

  const supabase = createClientBrowser();

  useEffect(() => {
    // Check for error parameters in the URL hash
    const hash = window.location.hash;
    const urlParams = new URLSearchParams(hash.substring(1));

    const error = urlParams.get('error');
    const errorCode = urlParams.get('error_code');
    const errorDescription = urlParams.get('error_description');

    if (error) {
      // Handle specific error cases
      if (errorCode === 'otp_expired') {
        setError(
          'Link de confirmação expirado. Solicite um novo e-mail de confirmação.'
        );
      } else if (errorCode === 'access_denied') {
        setError('Acesso negado. O link pode estar inválido ou já foi usado.');
      } else {
        setError(errorDescription || 'Erro na confirmação do e-mail');
      }
      setLoading(false);
      return;
    }

    // Check if this is a valid confirmation
    const token = searchParams?.get('token');
    const type = searchParams?.get('type');

    if (type === 'signup' && token) {
      // Email confirmation was successful
      setLoading(false);
    } else {
      setError('Link de confirmação inválido ou expirado');
      setLoading(false);
    }
  }, [searchParams]);

  const handleResendConfirmation = async () => {
    setResendingEmail(true);
    setError(null);

    try {
      // Get email from URL parameters or prompt user
      const email =
        searchParams?.get('email') ||
        prompt('Digite seu e-mail para reenviar a confirmação:');

      if (!email) {
        setError('E-mail e obrigatório para reenviar a confirmação');
        setResendingEmail(false);
        return;
      }

      const { error: resendError } = await supabase.auth.resend({
        type: 'signup',
        email: email,
      });

      if (resendError) throw resendError;

      setError(
        'E-mail de confirmação reenviado! Verifique sua caixa de entrada.'
      );
    } catch (err: any) {
      setError(err.message);
    } finally {
      setResendingEmail(false);
    }
  };

  if (loading) {
    return (
      <div className='flex min-h-screen items-center justify-center'>
        <div className='text-center'>
          <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-finance-primary-600 mx-auto'></div>
          <p className='mt-2 text-muted-foreground'>
            Verificando confirmacao...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='flex min-h-screen flex-col'>
        <div className='flex flex-1 items-center justify-center p-4'>
          <div className='w-full max-w-md space-y-8'>
            <div className='flex flex-col items-center text-center'>
              <div className='flex items-center gap-3 mb-4'>
                <Image
                  src={noBackground}
                  alt='Zomma Quant Logo'
                  width={120}
                  height={120}
                  className='h-12 w-auto'
                />
              </div>
              <h1 className='mt-3 text-3xl font-bold text-finance-danger-500'>
                Erro na confirmação
              </h1>
            </div>

            <Card>
              <CardContent className='pt-6'>
                <div className='flex flex-col items-center space-y-4 text-center'>
                  <div className='rounded-full bg-finance-danger-500/10 p-3'>
                    <Mail className='h-6 w-6 text-finance-danger-500' />
                  </div>
                  <div className='space-y-2'>
                    <h3 className='text-lg font-semibold'>
                      Problema na confirmação
                    </h3>
                    <p className='text-sm text-muted-foreground'>{error}</p>
                  </div>
                </div>
              </CardContent>
              <CardHeader className='pt-0'>
                <div className='space-y-4'>
                  <Button
                    onClick={handleResendConfirmation}
                    variant='outline'
                    className='w-full'
                    disabled={resendingEmail}
                  >
                    {resendingEmail ? (
                      <>
                        <RefreshCw className='mr-2 h-4 w-4 animate-spin' />
                        Enviando...
                      </>
                    ) : (
                      <>
                        <Mail className='mr-2 h-4 w-4' />
                        Reenviar e-mail de confirmação
                      </>
                    )}
                  </Button>

                  <div className='text-center'>
                    <Button
                      variant='ghost'
                      onClick={() => router.push('/auth/login')}
                      className='text-finance-secondary-600 underline-offset-4 hover:underline'
                    >
                      Voltar para o Login
                    </Button>
                  </div>
                </div>
              </CardHeader>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className='flex min-h-screen flex-col'>
      <div className='flex flex-1 items-center justify-center p-4'>
        <div className='w-full max-w-md space-y-8'>
          <div className='flex flex-col items-center text-center'>
            <div className='flex items-center gap-3 mb-4'>
              <Image
                src='/Logofiles/For Web/svg/White logo - no background.svg'
                alt='Zomma Quant Logo'
                width={120}
                height={120}
                className='h-12 w-auto'
              />
            </div>
            <h1 className='mt-3 text-3xl font-bold'>E-mail confirmado!</h1>
            <p className='mt-2 text-muted-foreground'>
              Sua conta foi ativada com sucesso!
            </p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className='text-center'>
                Bem-vindo ao Zomma Quant!
              </CardTitle>
            </CardHeader>
            <CardContent className='pt-6'>
              <div className='flex flex-col items-center space-y-4 text-center'>
                <div className='rounded-full bg-finance-success-500/10 p-3'>
                  <CheckCircle className='h-6 w-6 text-finance-success-500' />
                </div>
                <div className='space-y-2'>
                  <h3 className='text-lg font-semibold'>Conta Ativada</h3>
                  <p className='text-sm text-muted-foreground'>
                    Seu e-mail foi confirmado com sucesso. Agora você tem acesso
                    completo a plataforma.
                  </p>
                </div>

                <div className='w-full space-y-3 mt-6'>
                  <div className='flex items-center space-x-3 text-sm'>
                    <CheckCircle className='h-4 w-4 text-finance-success-500' />
                    <span>Estratégias de trading quantitativo</span>
                  </div>
                  <div className='flex items-center space-x-3 text-sm'>
                    <CheckCircle className='h-4 w-4 text-finance-success-500' />
                    <span>Análise de mercado em tempo real</span>
                  </div>
                  <div className='flex items-center space-x-3 text-sm'>
                    <CheckCircle className='h-4 w-4 text-finance-success-500' />
                    <span>Ferramentas de backtesting</span>
                  </div>
                  <div className='flex items-center space-x-3 text-sm'>
                    <CheckCircle className='h-4 w-4 text-finance-success-500' />
                    <span>Comunidade de traders</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className='space-y-4'>
            <Button
              onClick={() => router.push('/dashboard')}
              className='w-full bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500'
            >
              Acessar Dashboard
              <ArrowRight className='ml-2 h-4 w-4' />
            </Button>

            <div className='text-center'>
              <p className='text-sm text-muted-foreground'>
                Precisa de ajuda?{' '}
                <a
                  href='mailto:suporte@zommaquant.com'
                  className='text-finance-secondary-600 underline-offset-4 hover:underline'
                >
                  Entre em contato
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

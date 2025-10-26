'use client';

import { ArrowRight, Mail, RefreshCw } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import noBackground from '../../../../public/logoFiles/web/png/colorLogoWithoutBackground.png';

import { createClientBrowser } from '@/lib/supabaseClient';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resendingConfirmation, setResendingConfirmation] = useState(false);

  const supabase = createClientBrowser();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { data, error: signInError } =
        await supabase.auth.signInWithPassword({
          email,
          password,
        });

      if (signInError) throw signInError;

      if (data.user) {
        router.push('/dashboard');
      }
    } catch (err: any) {
      // Handle specific email confirmation error
      if (err.message.includes('Email not confirmed')) {
        setError(
          'E-mail não confirmado. Verifique sua caixa de entrada e clique no link de confirmação.'
        );
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendConfirmation = async () => {
    if (!email) {
      setError('Digite seu e-mail primeiro');
      return;
    }

    setResendingConfirmation(true);
    setError(null);

    try {
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
      setResendingConfirmation(false);
    }
  };

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
            <h1 className='mt-3 text-3xl font-bold'>Bem-vindo de volta</h1>
            <p className='mt-2 text-muted-foreground'>
              Entre na sua plataforma de trading
            </p>
          </div>

          <Card>
            <form onSubmit={handleSubmit}>
              <CardContent className='pt-6'>
                <div className='space-y-4'>
                  {error && (
                    <div className='rounded-md bg-finance-danger-500/10 p-3 text-sm text-finance-danger-500'>
                      <div className='space-y-2'>
                        <p>{error}</p>
                        {error.includes('E-mail não confirmado') && (
                          <Button
                            onClick={handleResendConfirmation}
                            variant='outline'
                            size='sm'
                            className='h-8 text-xs'
                            disabled={resendingConfirmation}
                          >
                            {resendingConfirmation ? (
                              <>
                                <RefreshCw className='mr-1 h-3 w-3 animate-spin' />
                                Enviando...
                              </>
                            ) : (
                              <>
                                <Mail className='mr-1 h-3 w-3' />
                                Reenviar confirmação
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
                  )}
                  <div className='space-y-2'>
                    <Label htmlFor='email'>E-mail</Label>
                    <Input
                      id='email'
                      type='email'
                      placeholder='nome@exemplo.com'
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div className='space-y-2'>
                    <div className='flex items-center justify-between'>
                      <Label htmlFor='password'>Senha</Label>
                      <Link
                        href='/auth/forgot-password'
                        className='text-sm text-muted-foreground underline-offset-4 hover:underline'
                      >
                        Esqueceu a senha?
                      </Link>
                    </div>
                    <Input
                      id='password'
                      type='password'
                      placeholder='••••••••'
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  <div className='flex items-center space-x-2'>
                    <Checkbox id='remember' />
                    <Label htmlFor='remember' className='text-sm font-normal'>
                      Lembrar de mim
                    </Label>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  type='submit'
                  className='w-full bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500'
                  disabled={loading}
                >
                  {loading ? 'Entrando...' : 'Entrar'}
                  <ArrowRight className='ml-2 h-4 w-4' />
                </Button>
              </CardFooter>
            </form>
          </Card>

          <div className='text-center text-sm'>
            Não tem uma conta?{' '}
            <Link
              href='/auth/signup'
              className='text-finance-secondary-600 underline-offset-4 hover:underline'
            >
              Cadastrar-se
            </Link>
          </div>

          <div className='mt-6'>
            <div className='relative'>
              <div className='absolute inset-0 flex items-center'>
                <div className='w-full border-t'></div>
              </div>
              <div className='relative flex justify-center text-xs uppercase'>
                <span className='bg-background px-2 text-muted-foreground'>
                  Ou continue com
                </span>
              </div>
            </div>

            <div className='mt-4 grid grid-cols-2 gap-3'>
              <Button variant='outline' className='w-full'>
                Google
              </Button>
              <Button variant='outline' className='w-full'>
                Apple
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import { ArrowLeft, CheckCircle, Eye, EyeOff } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

// import { supabase } from '@/lib/supabase-old';
import { createClientBrowser } from '@/lib/supabaseClient';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import noBackground from '../../../../public/logoFiles/web/png/colorLogoWithoutBackground.png';

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const supabase = createClientBrowser();

  useEffect(() => {
    // Check if we have the necessary tokens in the URL
    const accessToken = searchParams?.get('access_token');
    const refreshToken = searchParams?.get('refresh_token');

    if (!accessToken || !refreshToken) {
      setError(
        'Link inválido ou expirado. Solicite um novo link de redefinição.'
      );
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('As senhas não conferem');
      setLoading(false);
      return;
    }

    // Validate password strength
    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres');
      setLoading(false);
      return;
    }

    try {
      const { error: updateError } = await supabase.auth.updateUser({
        password: password,
      });

      if (updateError) throw updateError;

      setSuccess(true);

      // Redirect to login after 3 seconds
      setTimeout(() => {
        router.push('/auth/login');
      }, 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
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
              <h1 className='mt-3 text-3xl font-bold'>Senha redefinida!</h1>
              <p className='mt-2 text-muted-foreground'>
                Sua senha foi alterada com sucesso
              </p>
            </div>

            <Card>
              <CardContent className='pt-6'>
                <div className='flex flex-col items-center space-y-4 text-center'>
                  <div className='rounded-full bg-finance-success-500/10 p-3'>
                    <CheckCircle className='h-6 w-6 text-finance-success-500' />
                  </div>
                  <div className='space-y-2'>
                    <h3 className='text-lg font-semibold'>
                      Redefinição concluída
                    </h3>
                    <p className='text-sm text-muted-foreground'>
                      Sua senha foi alterada com sucesso. Você será
                      redirecionado para o login.
                    </p>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  onClick={() => router.push('/auth/login')}
                  className='w-full bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500'
                >
                  Ir para o login
                </Button>
              </CardFooter>
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
                src={noBackground}
                alt='Zomma Quant Logo'
                width={120}
                height={120}
                className='h-12 w-auto'
              />
            </div>
            <h1 className='mt-3 text-3xl font-bold'>Nova senha</h1>
            <p className='mt-2 text-muted-foreground'>Digite sua nova senha</p>
          </div>

          <Card>
            <form onSubmit={handleSubmit}>
              <CardContent className='pt-6'>
                <div className='space-y-4'>
                  {error && (
                    <div className='rounded-md bg-finance-danger-500/10 p-3 text-sm text-finance-danger-500'>
                      {error}
                    </div>
                  )}
                  <div className='space-y-2'>
                    <Label htmlFor='password'>Nova senha</Label>
                    <div className='relative'>
                      <Input
                        id='password'
                        type={showPassword ? 'text' : 'password'}
                        placeholder='••••••••'
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                      />
                      <Button
                        type='button'
                        variant='ghost'
                        size='sm'
                        className='absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent'
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className='h-4 w-4' />
                        ) : (
                          <Eye className='h-4 w-4' />
                        )}
                      </Button>
                    </div>
                  </div>
                  <div className='space-y-2'>
                    <Label htmlFor='confirmPassword'>
                      Confirme a nova senha
                    </Label>
                    <div className='relative'>
                      <Input
                        id='confirmPassword'
                        type={showConfirmPassword ? 'text' : 'password'}
                        placeholder='••••••••'
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                      />
                      <Button
                        type='button'
                        variant='ghost'
                        size='sm'
                        className='absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent'
                        onClick={() =>
                          setShowConfirmPassword(!showConfirmPassword)
                        }
                      >
                        {showConfirmPassword ? (
                          <EyeOff className='h-4 w-4' />
                        ) : (
                          <Eye className='h-4 w-4' />
                        )}
                      </Button>
                    </div>
                  </div>
                  <div className='text-xs text-muted-foreground'>
                    <p>A senha deve ter pelo menos 6 caracteres</p>
                  </div>
                </div>
              </CardContent>
              <CardFooter className='flex flex-col gap-4'>
                <Button
                  type='submit'
                  className='w-full bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500'
                  disabled={loading}
                >
                  {loading ? 'Redefinindo...' : 'Redefinir senha'}
                </Button>
                <div className='text-center'>
                  <Link
                    href='/auth/login'
                    className='text-sm text-finance-secondary-600 underline-offset-4 hover:underline flex items-center justify-center gap-2'
                  >
                    <ArrowLeft className='h-4 w-4' />
                    Voltar para o login
                  </Link>
                </div>
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
}

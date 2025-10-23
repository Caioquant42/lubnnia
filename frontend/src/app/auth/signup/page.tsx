'use client';

import { Mail, RefreshCw } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { supabase } from '@/lib/supabase';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function SignupPage() {
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState<'FREE' | 'ZOMMA_PRO'>(
    'FREE'
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  // Format phone number as (99) 99999-9999
  const formatPhoneNumber = (value: string) => {
    if (!value) return value;

    // Remove all non-numeric characters
    const phoneNumber = value.replace(/\D/g, '');

    // Apply the mask
    if (phoneNumber.length <= 2) {
      return `(${phoneNumber}`;
    } else if (phoneNumber.length <= 7) {
      return `(${phoneNumber.slice(0, 2)}) ${phoneNumber.slice(2)}`;
    } else {
      return `(${phoneNumber.slice(0, 2)}) ${phoneNumber.slice(2, 7)}-${phoneNumber.slice(7, 11)}`;
    }
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formattedPhoneNumber = formatPhoneNumber(e.target.value);
    setFormData({
      ...formData,
      phone: formattedPhoneNumber,
    });
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    // Validate password match
    if (formData.password !== formData.confirmPassword) {
      setError('As senhas não conferem');
      setLoading(false);
      return;
    }

    try {
      // Sign up with email and password
      const { data, error: signUpError } = await supabase.auth.signUp({
        email: formData.email,
        password: formData.password,
        options: {
          data: {
            full_name: formData.fullName,
            phone: formData.phone,
            plan: selectedPlan,
          },
        },
      });

      if (signUpError) throw signUpError;

      if (data.user) {
        // Check if email confirmation is required
        if (data.user.email_confirmed_at === null) {
          setSuccess(true);
        } else {
          // Email already confirmed, redirect to dashboard
          if (selectedPlan !== 'FREE') {
            router.push(`/checkout?plan=${selectedPlan}`);
          } else {
            router.push('/dashboard');
          }
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleResendConfirmation = async () => {
    setLoading(true);
    setError(null);

    try {
      const { error: resendError } = await supabase.auth.resend({
        type: 'signup',
        email: formData.email,
      });

      if (resendError) throw resendError;

      // Show success message
      setError(null);
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
                  src='/Logofiles/For Web/svg/White logo - no background.svg'
                  alt='Zomma Quant Logo'
                  width={120}
                  height={120}
                  className='h-12 w-auto'
                />
              </div>
              <h1 className='mt-3 text-3xl font-bold'>Confirme seu e-mail</h1>
              <p className='mt-2 text-muted-foreground'>
                Verifique sua caixa de entrada
              </p>
            </div>

            <Card>
              <CardContent className='pt-6'>
                <div className='flex flex-col items-center space-y-4 text-center'>
                  <div className='rounded-full bg-finance-success-500/10 p-3'>
                    <Mail className='h-6 w-6 text-finance-success-500' />
                  </div>
                  <div className='space-y-2'>
                    <h3 className='text-lg font-semibold'>
                      E-mail de confirmação enviado
                    </h3>
                    <p className='text-sm text-muted-foreground'>
                      Enviamos um link de confirmação para{' '}
                      <span className='font-medium'>{formData.email}</span>
                    </p>
                  </div>
                  <div className='text-sm text-muted-foreground'>
                    <p>Verifique sua caixa de entrada e spam.</p>
                    <p>Clique no link para confirmar sua conta.</p>
                  </div>
                </div>
              </CardContent>
              <CardFooter className='flex flex-col gap-4'>
                <Button
                  onClick={handleResendConfirmation}
                  variant='outline'
                  className='w-full'
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <RefreshCw className='mr-2 h-4 w-4 animate-spin' />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Mail className='mr-2 h-4 w-4' />
                      Reenviar e-mail
                    </>
                  )}
                </Button>
                <div className='text-center'>
                  <Link
                    href='/auth/login'
                    className='text-sm text-finance-secondary-600 underline-offset-4 hover:underline'
                  >
                    Voltar para o login
                  </Link>
                </div>
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
                src='/Logofiles/For Web/svg/White logo - no background.svg'
                alt='Zomma Quant Logo'
                width={120}
                height={120}
                className='h-12 w-auto'
              />
            </div>
            <h1 className='mt-3 text-3xl font-bold'>Crie sua conta</h1>
            <p className='mt-2 text-muted-foreground'>
              Registre-se agora para começar sua jornada de trading
            </p>
          </div>

          <Card>
            <form onSubmit={handleSubmit}>
              <CardContent className='pt-6'>
                <div className='space-y-4'>
                  {' '}
                  {error && (
                    <div className='rounded-md bg-finance-danger-500/10 p-3 text-sm text-finance-danger-500'>
                      {error}
                    </div>
                  )}
                  <div className='space-y-2'>
                    <Label htmlFor='fullName'>Nome Completo</Label>
                    <Input
                      id='fullName'
                      name='fullName'
                      type='text'
                      placeholder='João da Silva'
                      required
                      value={formData.fullName}
                      onChange={handleChange}
                    />
                  </div>
                  <div className='space-y-2'>
                    <Label htmlFor='email'>E-mail</Label>
                    <Input
                      id='email'
                      name='email'
                      type='email'
                      placeholder='nome@exemplo.com'
                      required
                      value={formData.email}
                      onChange={handleChange}
                    />
                  </div>
                  <div className='space-y-2'>
                    <Label htmlFor='phone'>Telefone</Label>
                    <Input
                      id='phone'
                      name='phone'
                      type='tel'
                      placeholder='(99) 99999-9999'
                      required
                      value={formData.phone}
                      onChange={handlePhoneChange}
                    />
                  </div>
                  <div className='space-y-2'>
                    <Label htmlFor='password'>Senha</Label>
                    <Input
                      id='password'
                      name='password'
                      type='password'
                      placeholder='••••••••'
                      required
                      value={formData.password}
                      onChange={handleChange}
                    />
                  </div>
                  <div className='space-y-2'>
                    <Label htmlFor='confirmPassword'>Confirme a Senha</Label>
                    <Input
                      id='confirmPassword'
                      name='confirmPassword'
                      type='password'
                      placeholder='••••••••'
                      required
                      value={formData.confirmPassword}
                      onChange={handleChange}
                    />
                  </div>
                  <div className='space-y-3'>
                    <Label>Plano</Label>
                    <div className='flex items-center space-x-2 rounded-md border p-3 bg-finance-secondary-50'>
                      <div className='flex-1 text-finance-primary-800 font-medium'>
                        Acesso Completo & Gratuito.
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>

              <CardFooter className='flex flex-col gap-4'>
                <Button
                  type='submit'
                  className='w-full bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500'
                  disabled={loading}
                >
                  {loading ? 'Processando...' : 'Criar Conta'}
                </Button>
                <div className='text-center text-sm'>
                  Já tem uma conta?{' '}
                  <Link
                    href='/auth/login'
                    className='text-finance-secondary-500 underline-offset-4 hover:underline'
                  >
                    Entrar
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

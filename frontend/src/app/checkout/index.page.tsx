'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';

import { createCheckoutSession } from '@/lib/stripe';
import { STRIPE_PRODUCTS } from '@/stripe-config';

export default function CheckoutPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const plan = searchParams?.get('plan');

    if (!plan || !(plan in STRIPE_PRODUCTS)) {
      setError('Invalid plan selected');
      setLoading(false);
      return;
    }

    const product = STRIPE_PRODUCTS[plan as keyof typeof STRIPE_PRODUCTS];

    createCheckoutSession(product.priceId, product.mode)
      .then((url) => {
        if (url) {
          window.location.href = url;
        } else {
          throw new Error('No checkout URL received');
        }
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [searchParams]);

  if (error) {
    return (
      <div className='flex min-h-[400px] items-center justify-center'>
        <div className='text-center'>
          <h1 className='text-xl font-semibold text-finance-danger-500'>
            Error
          </h1>
          <p className='mt-2 text-muted-foreground'>{error}</p>
          <button
            onClick={() => router.push('/pricing')}
            className='mt-4 text-sm text-finance-secondary-600 hover:underline'
          >
            Return to pricing
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className='flex min-h-[400px] items-center justify-center'>
      <div className='text-center'>
        <Loader2 className='mx-auto h-8 w-8 animate-spin text-finance-secondary-400' />
        <p className='mt-4 text-muted-foreground'>
          Preparing your checkout session...
        </p>
      </div>
    </div>
  );
}

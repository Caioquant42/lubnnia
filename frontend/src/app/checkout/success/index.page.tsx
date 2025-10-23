import { Check } from 'lucide-react';
import Link from 'next/link';

import { Button } from '@/components/ui/button';

export default function CheckoutSuccessPage() {
  return (
    <div className='container flex min-h-[400px] items-center justify-center'>
      <div className='mx-auto max-w-md text-center'>
        <div className='mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-finance-success-500/20'>
          <Check className='h-6 w-6 text-finance-success-500' />
        </div>
        <h1 className='text-2xl font-semibold'>Thank You!</h1>
        <p className='mt-2 text-muted-foreground'>
          Your payment was successful and your subscription is now active.
        </p>
        <div className='mt-6'>
          <Button
            asChild
            className='bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500'
          >
            <Link href='/dashboard'>Go to Dashboard</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}

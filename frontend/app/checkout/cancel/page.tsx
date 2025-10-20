import Link from 'next/link';
import { XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function CheckoutCancelPage() {
  return (
    <div className="container flex min-h-[400px] items-center justify-center">
      <div className="mx-auto max-w-md text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-finance-danger-500/20">
          <XCircle className="h-6 w-6 text-finance-danger-500" />
        </div>
        <h1 className="text-2xl font-semibold">Payment Cancelled</h1>
        <p className="mt-2 text-muted-foreground">
          Your payment was cancelled. No charges were made.
        </p>
        <div className="mt-6">
          <Button
            asChild
            className="bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500"
          >
            <Link href="/pricing">Return to Pricing</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
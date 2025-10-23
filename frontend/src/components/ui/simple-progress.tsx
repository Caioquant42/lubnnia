'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

// A simple progress component that doesn't rely on @radix-ui/react-progress
const SimpleProgress = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { value?: number }
>(({ className, value = 0, ...props }, ref) => {
  const percentage = Math.min(Math.max(value, 0), 100);
  
  return (
    <div
      ref={ref}
      className={cn(
        'relative h-4 w-full overflow-hidden rounded-full bg-secondary',
        className
      )}
      {...props}
    >
      <div
        className="h-full w-full flex-1 bg-primary transition-all"
        style={{ transform: `translateX(-${100 - percentage}%)` }}
      />
    </div>
  );
});

SimpleProgress.displayName = 'SimpleProgress';

export { SimpleProgress };

// Type declarations for Deno-specific imports
declare module 'npm:stripe@*' {
  import Stripe from 'stripe';
  export default Stripe;
}

declare module 'npm:@supabase/supabase-js@*' {
  export * from '@supabase/supabase-js';
}

// Add Deno namespace for env access
declare namespace Deno {
  export interface Env {
    get(key: string): string | undefined;
  }
  export const env: Env;
}

// Type definitions for Deno APIs used in Edge Functions

// Include DOM types for Request and Response
/// <reference lib="dom" />

declare namespace Deno {
  export interface ServeOptions {
    port?: number;
    hostname?: string;
  }

  export type ServeHandler = (request: Request) => Response | Promise<Response>;

  export function serve(
    handler: ServeHandler,
    options?: ServeOptions
  ): void;

  export const env: {
    get(key: string): string | undefined;
    set(key: string, value: string): void;
    toObject(): { [key: string]: string };
  };
}

// Add declarations for npm: imports
declare module 'npm:stripe@17.7.0' {
  const Stripe: any;
  export default Stripe;
}

declare module 'npm:@supabase/supabase-js@2.49.1' {
  export const createClient: any;
}

// Ensure global fetch types are available
declare global {
  interface RequestInit {
    method?: string;
    headers?: Record<string, string>;
    body?: string;
  }
}

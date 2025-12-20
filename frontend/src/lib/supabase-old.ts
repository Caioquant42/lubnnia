/**
 * Supabase Client Configuration
 * Initializes and exports the Supabase client for authentication and database operations
 */

import { createClient } from '@supabase/supabase-js';

// Supabase configuration from environment variables
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

// Validate that required environment variables are present
if (!supabaseUrl) {
  console.error('Missing NEXT_PUBLIC_SUPABASE_URL environment variable');
}

console.log('URL do Supabase:', process.env.NEXT_PUBLIC_SUPABASE_URL);

if (!supabaseAnonKey) {
  console.error('Missing NEXT_PUBLIC_SUPABASE_ANON_KEY environment variable');
}

/**
 * Supabase client instance
 * Used throughout the application for authentication, database queries, and real-time subscriptions
 *
 * @example
 * // Authentication
 * const { data, error } = await supabase.auth.signIn({ email, password })
 *
 * @example
 * // Database query
 * const { data, error } = await supabase.from('table_name').select('*')
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});

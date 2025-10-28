import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';

export const createClient = async () => {
  console.log('SUPABASE URL:', process.env.NEXT_PUBLIC_SUPABASE_URL);
  console.log('SUPABASE KEY:', process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // Ignora erro em Server Components
          }
        },
      },
    }
  );
};

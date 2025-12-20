# Email Authentication

This project uses Supabase's email-based authentication. Username-based authentication has been removed in favor of a simpler, more secure approach.

## Implementation Details

- Users register with an email address, password, and profile details
- Login is handled via email address only
- User metadata is stored in the profiles table, linked to the auth.users table

## Profiles Table Schema

```sql
CREATE TABLE public.profiles (
  id UUID NOT NULL PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  phone TEXT,
  plan TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);
```

## Setting Up the Profiles Table

1. The profiles table is created automatically via migration
2. Run the migration script:

```bash
node scripts/apply_profiles_migration.js
```

## Row-Level Security

The profiles table implements row-level security to ensure users can only access their own profile data:

```sql
-- Users can view their own profile
CREATE POLICY "Users can view own profile"
  ON public.profiles
  FOR SELECT
  USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON public.profiles
  FOR UPDATE
  USING (auth.uid() = id);
```
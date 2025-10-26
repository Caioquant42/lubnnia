/**
 * User Permissions and Access Control
 * Manages tier-based access to different applications/features
 */

// import { supabase } from './supabase-old';
import { createClientBrowser } from './supabaseClient';

const supabase = createClientBrowser();

/**
 * Available application IDs for access control
 */
export type ApplicationId =
  | 'screener'
  | 'options'
  | 'collar'
  | 'coveredcall'
  | 'pairs-trading'
  | 'rrg'
  | 'volatility'
  | 'recommendations'
  | 'retirement'
  | 'portfolio'
  | 'market-data'
  | 'dividend-calendar';

/**
 * User tier levels
 */
export enum UserTier {
  FREE = 'free',
  BASIC = 'basic',
  PREMIUM = 'premium',
  ENTERPRISE = 'enterprise',
}

/**
 * Application access mapping by tier
 * Defines which applications are available for each tier level
 */
const TIER_PERMISSIONS: Record<UserTier, ApplicationId[]> = {
  [UserTier.FREE]: ['market-data', 'dividend-calendar'],
  [UserTier.BASIC]: [
    'market-data',
    'dividend-calendar',
    'screener',
    'recommendations',
    'retirement',
  ],
  [UserTier.PREMIUM]: [
    'market-data',
    'dividend-calendar',
    'screener',
    'recommendations',
    'retirement',
    'options',
    'collar',
    'coveredcall',
    'volatility',
    'portfolio',
  ],
  [UserTier.ENTERPRISE]: [
    'market-data',
    'dividend-calendar',
    'screener',
    'recommendations',
    'retirement',
    'options',
    'collar',
    'coveredcall',
    'volatility',
    'portfolio',
    'pairs-trading',
    'rrg',
  ],
};

/**
 * Get the current user's tier from Supabase
 *
 * @returns The user's tier level or FREE if not authenticated
 */
async function getUserTier(): Promise<UserTier> {
  try {
    const {
      data: { user },
    } = await supabase.auth.getUser();

    if (!user) {
      return UserTier.FREE;
    }

    // Try to get tier from user metadata
    const tierFromMetadata = user.user_metadata?.tier as string;
    if (
      tierFromMetadata &&
      Object.values(UserTier).includes(tierFromMetadata as UserTier)
    ) {
      return tierFromMetadata as UserTier;
    }

    // Try to get tier from profiles table
    try {
      const { data: profile, error } = await supabase
        .from('profiles')
        .select('tier')
        .eq('id', user.id)
        .single();

      if (!error && profile?.tier) {
        return profile.tier as UserTier;
      }
    } catch (profileError) {
      console.warn('Could not fetch user profile, defaulting to FREE tier');
    }

    // Default to FREE tier if not specified
    return UserTier.FREE;
  } catch (error) {
    console.error('Error getting user tier:', error);
    return UserTier.FREE;
  }
}

/**
 * Check if the current user has access to a specific application
 *
 * @param applicationId - The ID of the application to check access for
 * @returns True if the user has access, false otherwise
 *
 * @example
 * const canAccessPairsTrading = await hasApplicationAccess('pairs-trading');
 * if (!canAccessPairsTrading) {
 *   router.push('/pricing');
 * }
 */
export async function hasApplicationAccess(
  applicationId: ApplicationId
): Promise<boolean> {
  try {
    const userTier = await getUserTier();
    const allowedApps = TIER_PERMISSIONS[userTier] || [];
    return allowedApps.includes(applicationId);
  } catch (error) {
    console.error('Error checking application access:', error);
    // Default to denying access on error for security
    return false;
  }
}

/**
 * Get all applications the current user has access to
 *
 * @returns Array of application IDs the user can access
 */
export async function getUserApplications(): Promise<ApplicationId[]> {
  try {
    const userTier = await getUserTier();
    return TIER_PERMISSIONS[userTier] || [];
  } catch (error) {
    console.error('Error getting user applications:', error);
    return TIER_PERMISSIONS[UserTier.FREE];
  }
}

/**
 * Check if user needs to upgrade to access an application
 *
 * @param applicationId - The application to check
 * @returns The minimum tier required, or null if already has access
 */
export async function getRequiredTierForApp(
  applicationId: ApplicationId
): Promise<UserTier | null> {
  const hasAccess = await hasApplicationAccess(applicationId);

  if (hasAccess) {
    return null;
  }

  // Find the minimum tier that has access to this app
  for (const [tier, apps] of Object.entries(TIER_PERMISSIONS)) {
    if (apps.includes(applicationId)) {
      return tier as UserTier;
    }
  }

  return UserTier.ENTERPRISE;
}

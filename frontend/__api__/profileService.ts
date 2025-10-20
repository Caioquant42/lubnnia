import { supabase } from '@/lib/supabase';

export interface ProfileFormData {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  bio: string;
  company: string;
  website: string;
  timezone: string;
}

export interface NotificationSettings {
  emailAlerts: boolean;
  pushNotifications: boolean;
  marketUpdates: boolean;
  portfolioAlerts: boolean;
  newsDigest: boolean;
  tradingSignals: boolean;
}

export interface SecuritySettings {
  twoFactorAuth: boolean;
  sessionTimeout: string;
  loginAlerts: boolean;
}

export interface ProfileUpdateResponse {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
}

class ProfileService {
  /**
   * Update user profile information in Supabase
   */
  async updateProfile(userId: string, profileData: ProfileFormData): Promise<ProfileUpdateResponse> {
    try {
      // Update user metadata in auth.users
      const { error: authError } = await supabase.auth.updateUser({
        data: {
          full_name: profileData.fullName,
          phone: profileData.phone,
          location: profileData.location,
          bio: profileData.bio,
          company: profileData.company,
          website: profileData.website,
          timezone: profileData.timezone,
        }
      });

      if (authError) {
        throw authError;
      }

      // Also update the profiles table if it exists
      try {
        const { error: profileError } = await supabase
          .from('profiles')
          .upsert({
            id: userId,
            full_name: profileData.fullName,
            phone: profileData.phone,
            location: profileData.location,
            bio: profileData.bio,
            company: profileData.company,
            website: profileData.website,
            timezone: profileData.timezone,
            updated_at: new Date().toISOString(),
          });

        if (profileError) {
          console.warn('Profile table update failed, but auth update succeeded:', profileError);
        }
      } catch (profileError) {
        console.warn('Profile table not available, auth update succeeded');
      }

      return {
        success: true,
        message: 'Perfil atualizado com sucesso!',
        data: profileData
      };
    } catch (error: any) {
      console.error('Error updating profile:', error);
      return {
        success: false,
        message: 'Erro ao atualizar perfil',
        error: error.message
      };
    }
  }

  /**
   * Update notification settings in Supabase
   */
  async updateNotificationSettings(userId: string, settings: NotificationSettings): Promise<ProfileUpdateResponse> {
    try {
      // Update user metadata with notification settings
      const { error: authError } = await supabase.auth.updateUser({
        data: {
          notification_settings: settings
        }
      });

      if (authError) {
        throw authError;
      }

      // Also update the profiles table if it exists
      try {
        const { error: profileError } = await supabase
          .from('profiles')
          .upsert({
            id: userId,
            notification_settings: settings,
            updated_at: new Date().toISOString(),
          });

        if (profileError) {
          console.warn('Profile table update failed, but auth update succeeded:', profileError);
        }
      } catch (profileError) {
        console.warn('Profile table not available, auth update succeeded');
      }

      return {
        success: true,
        message: 'Configurações de notificação atualizadas com sucesso!',
        data: settings
      };
    } catch (error: any) {
      console.error('Error updating notification settings:', error);
      return {
        success: false,
        message: 'Erro ao atualizar configurações de notificação',
        error: error.message
      };
    }
  }

  /**
   * Update security settings in Supabase
   */
  async updateSecuritySettings(userId: string, settings: SecuritySettings): Promise<ProfileUpdateResponse> {
    try {
      // Update user metadata with security settings
      const { error: authError } = await supabase.auth.updateUser({
        data: {
          security_settings: settings
        }
      });

      if (authError) {
        throw authError;
      }

      // Also update the profiles table if it exists
      try {
        const { error: profileError } = await supabase
          .from('profiles')
          .upsert({
            id: userId,
            security_settings: settings,
            updated_at: new Date().toISOString(),
          });

        if (profileError) {
          console.warn('Profile table update failed, but auth update succeeded:', profileError);
        }
      } catch (profileError) {
        console.warn('Profile table not available, auth update succeeded');
      }

      return {
        success: true,
        message: 'Configurações de segurança atualizadas com sucesso!',
        data: settings
      };
    } catch (error: any) {
      console.error('Error updating security settings:', error);
      return {
        success: false,
        message: 'Erro ao atualizar configurações de segurança',
        error: error.message
      };
    }
  }

  /**
   * Upload profile picture to Supabase Storage
   */
  async uploadProfilePicture(userId: string, file: File): Promise<ProfileUpdateResponse> {
    try {
      const fileExt = file.name.split('.').pop();
      const fileName = `${userId}-${Date.now()}.${fileExt}`;
      const filePath = `profile-pictures/${fileName}`;

      // Upload file to Supabase Storage
      const { error: uploadError } = await supabase.storage
        .from('avatars')
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: true
        });

      if (uploadError) {
        throw uploadError;
      }

      // Get public URL
      const { data: { publicUrl } } = supabase.storage
        .from('avatars')
        .getPublicUrl(filePath);

      // Update user metadata with new avatar URL
      const { error: updateError } = await supabase.auth.updateUser({
        data: {
          avatar_url: publicUrl
        }
      });

      if (updateError) {
        throw updateError;
      }

      // Also update the profiles table if it exists
      try {
        const { error: profileError } = await supabase
          .from('profiles')
          .upsert({
            id: userId,
            avatar_url: publicUrl,
            updated_at: new Date().toISOString(),
          });

        if (profileError) {
          console.warn('Profile table update failed, but auth update succeeded:', profileError);
        }
      } catch (profileError) {
        console.warn('Profile table not available, auth update succeeded');
      }

      return {
        success: true,
        message: 'Foto de perfil atualizada com sucesso!',
        data: { avatar_url: publicUrl }
      };
    } catch (error: any) {
      console.error('Error uploading profile picture:', error);
      return {
        success: false,
        message: 'Erro ao fazer upload da foto de perfil',
        error: error.message
      };
    }
  }

  /**
   * Get user profile data from Supabase
   */
  async getProfile(userId: string): Promise<ProfileUpdateResponse> {
    try {
      // Try to get from profiles table first
      try {
        const { data: profileData, error: profileError } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', userId)
          .single();

        if (profileData && !profileError) {
          return {
            success: true,
            message: 'Perfil carregado com sucesso',
            data: profileData
          };
        }
      } catch (profileError) {
        console.warn('Profile table not available, falling back to auth metadata');
      }

      // Fallback to auth metadata
      const { data: { user }, error: authError } = await supabase.auth.getUser();
      
      if (authError || !user) {
        throw new Error('User not found');
      }

      return {
        success: true,
        message: 'Perfil carregado com sucesso',
        data: {
          full_name: user.user_metadata?.full_name || '',
          email: user.email || '',
          phone: user.user_metadata?.phone || '',
          location: user.user_metadata?.location || '',
          bio: user.user_metadata?.bio || '',
          company: user.user_metadata?.company || '',
          website: user.user_metadata?.website || '',
          timezone: user.user_metadata?.timezone || 'America/Sao_Paulo',
          avatar_url: user.user_metadata?.avatar_url || '',
          notification_settings: user.user_metadata?.notification_settings || {},
          security_settings: user.user_metadata?.security_settings || {},
        }
      };
    } catch (error: any) {
      console.error('Error getting profile:', error);
      return {
        success: false,
        message: 'Erro ao carregar perfil',
        error: error.message
      };
    }
  }
}

export const profileService = new ProfileService();
export default profileService; 
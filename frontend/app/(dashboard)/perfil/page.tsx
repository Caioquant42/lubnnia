"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar, 
  Camera, 
  Bell, 
  Shield, 
  CreditCard, 
  Download,
  Edit2,
  Save,
  X,
  Loader2
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import profileService, { 
  ProfileFormData, 
  NotificationSettings, 
  SecuritySettings 
} from "@/__api__/profileService";

export default function ProfilePage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState("profile");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  // Profile form state
  const [profileData, setProfileData] = useState<ProfileFormData>({
    fullName: user?.user_metadata?.full_name || user?.name || "",
    email: user?.email || "",
    phone: user?.user_metadata?.phone || "",
    location: user?.user_metadata?.location || "",
    bio: user?.user_metadata?.bio || "",
    company: user?.user_metadata?.company || "",
    website: user?.user_metadata?.website || "",
    timezone: user?.user_metadata?.timezone || "America/Sao_Paulo",
  });

  // Notification settings state
  const [notifications, setNotifications] = useState<NotificationSettings>({
    emailAlerts: user?.user_metadata?.notification_settings?.emailAlerts ?? true,
    pushNotifications: user?.user_metadata?.notification_settings?.pushNotifications ?? true,
    marketUpdates: user?.user_metadata?.notification_settings?.marketUpdates ?? true,
    portfolioAlerts: user?.user_metadata?.notification_settings?.portfolioAlerts ?? true,
    newsDigest: user?.user_metadata?.notification_settings?.newsDigest ?? false,
    tradingSignals: user?.user_metadata?.notification_settings?.tradingSignals ?? true,
  });

  // Security settings state
  const [security, setSecurity] = useState<SecuritySettings>({
    twoFactorAuth: user?.user_metadata?.security_settings?.twoFactorAuth ?? false,
    sessionTimeout: user?.user_metadata?.security_settings?.sessionTimeout ?? "30",
    loginAlerts: user?.user_metadata?.security_settings?.loginAlerts ?? true,
  });

  // Load profile data on component mount
  useEffect(() => {
    if (user?.id) {
      loadProfileData();
    }
  }, [user?.id]);

  // Load profile data from Supabase
  const loadProfileData = async () => {
    if (!user?.id) return;
    
    setLoading(true);
    try {
      const response = await profileService.getProfile(user.id);
      if (response.success && response.data) {
        const data = response.data;
        setProfileData({
          fullName: data.full_name || "",
          email: data.email || "",
          phone: data.phone || "",
          location: data.location || "",
          bio: data.bio || "",
          company: data.company || "",
          website: data.website || "",
          timezone: data.timezone || "America/Sao_Paulo",
        });
        
        if (data.notification_settings) {
          setNotifications(data.notification_settings);
        }
        
        if (data.security_settings) {
          setSecurity(data.security_settings);
        }
      }
    } catch (error) {
      console.error('Error loading profile data:', error);
      toast({
        title: "Erro",
        description: "Não foi possível carregar os dados do perfil",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Save profile data to Supabase
  const handleProfileSave = async () => {
    if (!user?.id) return;
    
    setSaving(true);
    try {
      const response = await profileService.updateProfile(user.id, profileData);
      
      if (response.success) {
        toast({
          title: "Sucesso!",
          description: response.message,
        });
        setIsEditing(false);
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao salvar perfil",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      toast({
        title: "Erro",
        description: "Erro inesperado ao salvar perfil",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  // Save notification settings to Supabase
  const handleNotificationUpdate = async (key: keyof NotificationSettings, value: boolean) => {
    if (!user?.id) return;
    
    const newSettings = { ...notifications, [key]: value };
    setNotifications(newSettings);
    
    try {
      const response = await profileService.updateNotificationSettings(user.id, newSettings);
      
      if (response.success) {
        toast({
          title: "Sucesso!",
          description: response.message,
        });
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao atualizar configurações",
          variant: "destructive",
        });
        // Revert the change if it failed
        setNotifications(notifications);
      }
    } catch (error) {
      console.error('Error updating notification settings:', error);
      toast({
        title: "Erro",
        description: "Erro inesperado ao atualizar configurações",
        variant: "destructive",
      });
      // Revert the change if it failed
      setNotifications(notifications);
    }
  };

  // Save security settings to Supabase
  const handleSecurityUpdate = async (key: keyof SecuritySettings, value: boolean | string) => {
    if (!user?.id) return;
    
    const newSettings = { ...security, [key]: value };
    setSecurity(newSettings);
    
    try {
      const response = await profileService.updateSecuritySettings(user.id, newSettings);
      
      if (response.success) {
        toast({
          title: "Sucesso!",
          description: response.message,
        });
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao atualizar configurações",
          variant: "destructive",
        });
        // Revert the change if it failed
        setSecurity(security);
      }
    } catch (error) {
      console.error('Error updating security settings:', error);
      toast({
        title: "Erro",
        description: "Erro inesperado ao atualizar configurações",
        variant: "destructive",
      });
      // Revert the change if it failed
      setSecurity(security);
    }
  };

  // Handle profile picture upload
  const handleAvatarUpload = async (event: Event) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file || !user?.id) return;
    
    setUploading(true);
    try {
      const response = await profileService.uploadProfilePicture(user.id, file);
      
      if (response.success) {
        toast({
          title: "Sucesso!",
          description: response.message,
        });
        // Refresh the page to show the new avatar
        window.location.reload();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao fazer upload da foto",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error uploading avatar:', error);
      toast({
        title: "Erro",
        description: "Erro inesperado ao fazer upload da foto",
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  const accountCreatedDate = new Date(user?.user_metadata?.created_at || Date.now());
  const memberSince = accountCreatedDate.toLocaleDateString('pt-BR', { 
    year: 'numeric', 
    month: 'long'
  });

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Perfil do Usuário</h1>
          <p className="text-muted-foreground">
            Gerencie suas informações pessoais, configurações e preferências
          </p>
        </div>
        <Badge variant="secondary" className="bg-finance-primary-100 text-finance-primary-800">
          {user?.role === 'admin' ? 'Administrador' : 'Usuário'}
        </Badge>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="profile">Perfil</TabsTrigger>
          <TabsTrigger value="notifications">Notificações</TabsTrigger>
          <TabsTrigger value="security">Segurança</TabsTrigger>
          <TabsTrigger value="billing">Cobrança</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">Carregando perfil...</p>
              </div>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-3">
              {/* Avatar and Basic Info */}
              <Card className="md:col-span-1">
                <CardHeader>
                  <CardTitle>Foto do Perfil</CardTitle>
                  <CardDescription>
                    Sua foto será exibida em todo o sistema
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-col items-center space-y-4">
                    <Avatar className="h-32 w-32">
                      <AvatarImage 
                        src={user?.user_metadata?.avatar_url || ""} 
                        alt={profileData.fullName} 
                      />
                      <AvatarFallback className="bg-finance-primary-800 text-white text-2xl">
                        {profileData.fullName ? profileData.fullName[0].toUpperCase() : "U"}
                      </AvatarFallback>
                    </Avatar>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        const input = document.createElement('input');
                        input.type = 'file';
                        input.accept = 'image/*';
                        input.onchange = handleAvatarUpload;
                        input.click();
                      }}
                      className="w-full"
                      disabled={uploading}
                    >
                      {uploading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <Camera className="mr-2 h-4 w-4" />
                          Alterar Foto
                        </>
                      )}
                    </Button>
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-2">
                    <div className="flex items-center text-sm">
                      <Calendar className="mr-2 h-4 w-4 text-muted-foreground" />
                      <span>Membro desde {memberSince}</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <Mail className="mr-2 h-4 w-4 text-muted-foreground" />
                      <span>{user?.email}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Profile Form */}
              <Card className="md:col-span-2">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Informações Pessoais</CardTitle>
                      <CardDescription>
                        Atualize suas informações pessoais e de contato
                      </CardDescription>
                    </div>
                    <Button
                      variant={isEditing ? "outline" : "default"}
                      size="sm"
                      onClick={() => isEditing ? setIsEditing(false) : setIsEditing(true)}
                      disabled={loading || saving}
                    >
                      {loading || saving ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          {isEditing ? (
                            <>
                              <X className="mr-2 h-4 w-4" />
                              Cancelar
                            </>
                          ) : (
                            <>
                              <Edit2 className="mr-2 h-4 w-4" />
                              Editar
                            </>
                          )}
                        </>
                      )}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="fullName">Nome Completo</Label>
                      <Input
                        id="fullName"
                        value={profileData.fullName}
                        onChange={(e) => setProfileData(prev => ({ ...prev, fullName: e.target.value }))}
                        disabled={!isEditing || loading || saving}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={profileData.email}
                        disabled // Email usually shouldn't be editable
                        className={cn(isEditing && "bg-gray-50", "cursor-not-allowed")}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="phone">Telefone</Label>
                      <Input
                        id="phone"
                        value={profileData.phone}
                        onChange={(e) => setProfileData(prev => ({ ...prev, phone: e.target.value }))}
                        disabled={!isEditing || loading || saving}
                        placeholder="+55 (11) 9999-9999"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="location">Localização</Label>
                      <Input
                        id="location"
                        value={profileData.location}
                        onChange={(e) => setProfileData(prev => ({ ...prev, location: e.target.value }))}
                        disabled={!isEditing || loading || saving}
                        placeholder="São Paulo, Brazil"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="company">Empresa</Label>
                      <Input
                        id="company"
                        value={profileData.company}
                        onChange={(e) => setProfileData(prev => ({ ...prev, company: e.target.value }))}
                        disabled={!isEditing || loading || saving}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="website">Website</Label>
                      <Input
                        id="website"
                        value={profileData.website}
                        onChange={(e) => setProfileData(prev => ({ ...prev, website: e.target.value }))}
                        disabled={!isEditing || loading || saving}
                        placeholder="https://example.com"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="bio">Biografia</Label>
                    <Textarea
                      id="bio"
                      value={profileData.bio}
                      onChange={(e) => setProfileData(prev => ({ ...prev, bio: e.target.value }))}
                      disabled={!isEditing || loading || saving}
                      placeholder="Conte um pouco sobre você..."
                      className="resize-none"
                      rows={3}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="timezone">Fuso Horário</Label>
                    <Select 
                      value={profileData.timezone} 
                      onValueChange={(value) => setProfileData(prev => ({ ...prev, timezone: value }))}
                      disabled={!isEditing || loading || saving}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="America/Sao_Paulo">Brasília (GMT-3)</SelectItem>
                        <SelectItem value="America/New_York">New York (GMT-5)</SelectItem>
                        <SelectItem value="Europe/London">London (GMT+0)</SelectItem>
                        <SelectItem value="Asia/Tokyo">Tokyo (GMT+9)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {isEditing && (
                    <div className="flex justify-end pt-4">
                      <Button onClick={handleProfileSave} disabled={loading || saving}>
                        {loading || saving ? (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                          <>
                            <Save className="mr-2 h-4 w-4" />
                            Salvar Alterações
                          </>
                        )}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de Notificação</CardTitle>
              <CardDescription>
                Gerencie como e quando você quer receber notificações
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Alertas por Email</Label>
                    <p className="text-sm text-muted-foreground">
                      Receba notificações importantes por email
                    </p>
                  </div>
                  <Switch
                    checked={notifications.emailAlerts}
                    onCheckedChange={(checked) => handleNotificationUpdate('emailAlerts', checked)}
                    disabled={loading || saving}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Notificações Push</Label>
                    <p className="text-sm text-muted-foreground">
                      Receba notificações no navegador
                    </p>
                  </div>
                  <Switch
                    checked={notifications.pushNotifications}
                    onCheckedChange={(checked) => handleNotificationUpdate('pushNotifications', checked)}
                    disabled={loading || saving}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Atualizações de Mercado</Label>
                    <p className="text-sm text-muted-foreground">
                      Notificações sobre movimentos importantes do mercado
                    </p>
                  </div>
                  <Switch
                    checked={notifications.marketUpdates}
                    onCheckedChange={(checked) => handleNotificationUpdate('marketUpdates', checked)}
                    disabled={loading || saving}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Alertas de Portfólio</Label>
                    <p className="text-sm text-muted-foreground">
                      Notificações sobre mudanças no seu portfólio
                    </p>
                  </div>
                  <Switch
                    checked={notifications.portfolioAlerts}
                    onCheckedChange={(checked) => handleNotificationUpdate('portfolioAlerts', checked)}
                    disabled={loading || saving}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Resumo de Notícias</Label>
                    <p className="text-sm text-muted-foreground">
                      Resumo diário das principais notícias financeiras
                    </p>
                  </div>
                  <Switch
                    checked={notifications.newsDigest}
                    onCheckedChange={(checked) => handleNotificationUpdate('newsDigest', checked)}
                    disabled={loading || saving}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Sinais de Trading</Label>
                    <p className="text-sm text-muted-foreground">
                      Notificações sobre oportunidades de trading
                    </p>
                  </div>
                  <Switch
                    checked={notifications.tradingSignals}
                    onCheckedChange={(checked) => handleNotificationUpdate('tradingSignals', checked)}
                    disabled={loading || saving}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de Segurança</CardTitle>
              <CardDescription>
                Gerencie a segurança da sua conta e preferências de login
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Autenticação de Dois Fatores</Label>
                    <p className="text-sm text-muted-foreground">
                      Adicione uma camada extra de segurança à sua conta
                    </p>
                  </div>
                  <Switch
                    checked={security.twoFactorAuth}
                    onCheckedChange={(checked) => handleSecurityUpdate('twoFactorAuth', checked)}
                    disabled={loading || saving}
                  />
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label>Timeout da Sessão</Label>
                  <Select 
                    value={security.sessionTimeout} 
                    onValueChange={(value) => handleSecurityUpdate('sessionTimeout', value)}
                    disabled={!isEditing || loading || saving}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="15">15 minutos</SelectItem>
                      <SelectItem value="30">30 minutos</SelectItem>
                      <SelectItem value="60">1 hora</SelectItem>
                      <SelectItem value="240">4 horas</SelectItem>
                      <SelectItem value="never">Nunca</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-muted-foreground">
                    Tempo limite antes de fazer logout automático
                  </p>
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Alertas de Login</Label>
                    <p className="text-sm text-muted-foreground">
                      Notificações quando alguém faz login na sua conta
                    </p>
                  </div>
                  <Switch
                    checked={security.loginAlerts}
                    onCheckedChange={(checked) => handleSecurityUpdate('loginAlerts', checked)}
                    disabled={loading || saving}
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-lg font-medium">Alterar Senha</h3>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="currentPassword">Senha Atual</Label>
                    <Input id="currentPassword" type="password" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="newPassword">Nova Senha</Label>
                    <Input id="newPassword" type="password" />
                  </div>
                </div>
                <Button variant="outline">
                  <Shield className="mr-2 h-4 w-4" />
                  Alterar Senha
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Billing Tab */}
        <TabsContent value="billing" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Informações de Cobrança</CardTitle>
              <CardDescription>
                Gerencie sua assinatura e métodos de pagamento
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Current Plan */}
              <div className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">Plano Atual</h3>
                    <p className="text-sm text-muted-foreground">Plano Premium</p>
                  </div>
                  <Badge className="bg-finance-success-100 text-finance-success-800">
                    Ativo
                  </Badge>
                </div>
                <p className="mt-2 text-2xl font-bold">R$ 99,90/mês</p>
                <p className="text-sm text-muted-foreground">
                  Próxima cobrança: 24 de junho de 2025
                </p>
              </div>

              {/* Payment Method */}
              <div className="space-y-2">
                <Label>Método de Pagamento</Label>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div className="flex items-center space-x-3">
                    <CreditCard className="h-6 w-6 text-muted-foreground" />
                    <div>
                      <p className="font-medium">•••• •••• •••• 1234</p>
                      <p className="text-sm text-muted-foreground">Expira em 12/26</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Alterar
                  </Button>
                </div>
              </div>

              {/* Billing History */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Histórico de Cobrança</Label>
                  <Button variant="outline" size="sm">
                    <Download className="mr-2 h-4 w-4" />
                    Baixar Todas
                  </Button>
                </div>
                <div className="space-y-2">
                  {[
                    { date: "24 Mai 2025", amount: "R$ 99,90", status: "Pago" },
                    { date: "24 Abr 2025", amount: "R$ 99,90", status: "Pago" },
                    { date: "24 Mar 2025", amount: "R$ 99,90", status: "Pago" },
                  ].map((invoice, index) => (
                    <div key={index} className="flex items-center justify-between rounded-lg border p-3">
                      <div>
                        <p className="font-medium">{invoice.date}</p>
                        <p className="text-sm text-muted-foreground">{invoice.amount}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="secondary">{invoice.status}</Badge>
                        <Button variant="ghost" size="sm">
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

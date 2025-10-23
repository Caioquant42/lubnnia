# Supabase Email Customization Guide

## Overview
This guide explains how to customize the email confirmation process in Supabase to provide a better user experience with personalized emails and a custom confirmation page.

## Current Issue
The default Supabase confirmation email shows a generic "Supabase Auth" sender and basic styling, which doesn't reflect your brand identity.

## Solution: Custom Email Templates

### 1. Access Supabase Dashboard
1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **Authentication** > **Email Templates**

### 2. Customize the Confirmation Email Template

#### Subject Line
Replace the default subject with something more branded:
```
Welcome to Zomma Quant - Confirm Your Account
```

#### Email Body Template
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirm Your Zomma Quant Account</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            width: 120px;
            height: auto;
            margin-bottom: 20px;
        }
        h1 {
            color: #1a365d;
            font-size: 28px;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 16px;
            margin-bottom: 30px;
        }
        .content {
            margin-bottom: 30px;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 32px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            text-align: center;
            margin: 20px 0;
            transition: transform 0.2s;
        }
        .cta-button:hover {
            transform: translateY(-2px);
        }
        .footer {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        .security-note {
            background: #f0f9ff;
            border: 1px solid #bae6fd;
            border-radius: 8px;
            padding: 16px;
            margin: 20px 0;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bem-vindo ao Zomma Quant!</h1>
            <p class="subtitle">Sua plataforma de trading quantitativo</p>
        </div>
        
        <div class="content">
            <p>Olá,</p>
            <p>Obrigado por se cadastrar no Zomma Quant! Para ativar sua conta e começar a usar nossa plataforma, confirme seu endereço de e-mail clicando no botão abaixo:</p>
            
            <div style="text-align: center;">
                <a href="{{ .ConfirmationURL }}&redirect_to={{ .SiteURL }}/auth/email-confirmed" class="cta-button">
                    Confirmar E-mail
                </a>
            </div>
            
            <div class="security-note">
                <strong>Nota de Segurança:</strong> Este link expira em 24 horas por motivos de segurança. Se você não solicitou esta conta, pode ignorar este e-mail com segurança.
            </div>
            
            <p>Após confirmar seu e-mail, você terá acesso completo a:</p>
            <ul>
                <li>Estratégias de trading quantitativo</li>
                <li>Análise de mercado em tempo real</li>
                <li>Ferramentas de backtesting</li>
                <li>Comunidade de traders</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Se você não conseguir clicar no botão, copie e cole este link no seu navegador:</p>
            <p style="word-break: break-all; color: #667eea;">{{ .ConfirmationURL }}</p>
            
            <p style="margin-top: 20px;">
                <strong>Zomma Quant</strong><br>
                Plataforma de Trading Quantitativo<br>
                <a href="{{ .SiteURL }}" style="color: #667eea;">{{ .SiteURL }}</a>
            </p>
        </div>
    </div>
</body>
</html>
```

### 3. Create a Custom Confirmation Page

Create a new page in your Next.js app:

```typescript
// frontend/app/auth/email-confirmed/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { CheckCircle, ArrowRight, Mail } from "lucide-react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function EmailConfirmedPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if this is a valid confirmation
    const token = searchParams.get('token');
    const type = searchParams.get('type');
    
    if (type === 'signup' && token) {
      // Email confirmation was successful
      setLoading(false);
    } else {
      setError("Link de confirmação inválido ou expirado");
      setLoading(false);
    }
  }, [searchParams]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-finance-primary-600 mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Verificando confirmação...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen flex-col">
        <div className="flex flex-1 items-center justify-center p-4">
          <div className="w-full max-w-md space-y-8">
            <div className="flex flex-col items-center text-center">
              <div className="flex items-center gap-3 mb-4">
                <Image
                  src="/Logofiles/For Web/svg/White logo - no background.svg"
                  alt="Zomma Quant Logo"
                  width={120}
                  height={120}
                  className="h-12 w-auto"
                />
              </div>
              <h1 className="mt-3 text-3xl font-bold text-finance-danger-500">Erro na Confirmação</h1>
            </div>
            
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center space-y-4 text-center">
                  <div className="rounded-full bg-finance-danger-500/10 p-3">
                    <Mail className="h-6 w-6 text-finance-danger-500" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold">Link Inválido</h3>
                    <p className="text-sm text-muted-foreground">
                      {error}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <div className="flex flex-1 items-center justify-center p-4">
        <div className="w-full max-w-md space-y-8">
          <div className="flex flex-col items-center text-center">
            <div className="flex items-center gap-3 mb-4">
              <Image
                src="/Logofiles/For Web/svg/White logo - no background.svg"
                alt="Zomma Quant Logo"
                width={120}
                height={120}
                className="h-12 w-auto"
              />
            </div>
            <h1 className="mt-3 text-3xl font-bold">E-mail Confirmado!</h1>
            <p className="mt-2 text-muted-foreground">
              Sua conta foi ativada com sucesso
            </p>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-center">Bem-vindo ao Zomma Quant!</CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center space-y-4 text-center">
                <div className="rounded-full bg-finance-success-500/10 p-3">
                  <CheckCircle className="h-6 w-6 text-finance-success-500" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">Conta Ativada</h3>
                  <p className="text-sm text-muted-foreground">
                    Seu e-mail foi confirmado com sucesso. Agora você tem acesso completo à plataforma.
                  </p>
                </div>
                
                <div className="w-full space-y-3 mt-6">
                  <div className="flex items-center space-x-3 text-sm">
                    <CheckCircle className="h-4 w-4 text-finance-success-500" />
                    <span>Estratégias de trading quantitativo</span>
                  </div>
                  <div className="flex items-center space-x-3 text-sm">
                    <CheckCircle className="h-4 w-4 text-finance-success-500" />
                    <span>Análise de mercado em tempo real</span>
                  </div>
                  <div className="flex items-center space-x-3 text-sm">
                    <CheckCircle className="h-4 w-4 text-finance-success-500" />
                    <span>Ferramentas de backtesting</span>
                  </div>
                  <div className="flex items-center space-x-3 text-sm">
                    <CheckCircle className="h-4 w-4 text-finance-success-500" />
                    <span>Comunidade de traders</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <div className="space-y-4">
            <Button 
              onClick={() => router.push('/dashboard')}
              className="w-full bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500"
            >
              Acessar Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            
            <div className="text-center">
              <p className="text-sm text-muted-foreground">
                Precisa de ajuda?{" "}
                <a 
                  href="mailto:suporte@zommaquant.com" 
                  className="text-finance-secondary-600 underline-offset-4 hover:underline"
                >
                  Entre em contato
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 4. Configure Redirect URLs in Supabase

1. Go to **Authentication** > **Settings** in your Supabase Dashboard
2. Under **Redirect URLs**, add:
   ```
   http://localhost:3000/auth/email-confirmed
   https://yourdomain.com/auth/email-confirmed
   ```

### 5. Update Email Template with Redirect

Modify the confirmation link in your email template to include the redirect:

```html
<a href="{{ .ConfirmationURL }}&redirect_to={{ .SiteURL }}/auth/email-confirmed" class="cta-button">
    Confirmar E-mail
</a>
```

### 6. Environment Variables

Make sure your environment variables are set:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Additional Customizations

### Custom Email Templates for Other Flows

You can also customize:
- **Password Reset**: Reset password email template
- **Magic Link**: Magic link email template
- **Email Change**: Email change confirmation template

### Advanced Email Styling

For even more control, you can:
1. Use external email services (SendGrid, Mailgun, etc.)
2. Create custom email functions in Supabase Edge Functions
3. Use transactional email services with better deliverability

### Testing

1. Test the email template in Supabase Dashboard
2. Use a test email address to verify the flow
3. Check both desktop and mobile email clients
4. Verify the confirmation page loads correctly

## Benefits

- **Brand Consistency**: Emails match your application's design
- **Better UX**: Clear confirmation flow with branded pages
- **Professional Appearance**: No more generic "Supabase Auth" emails
- **User Trust**: Professional emails increase user confidence
- **Mobile Friendly**: Responsive email templates work on all devices

## Troubleshooting

### Common Issues

1. **Email not sending**: Check SMTP settings in Supabase
2. **Redirect not working**: Verify redirect URLs are properly configured
3. **Template not updating**: Clear browser cache and test with new email
4. **Styling issues**: Test in multiple email clients

### Support

For additional help:
- [Supabase Email Templates Documentation](https://supabase.com/docs/guides/auth/auth-email-templates)
- [Supabase Redirect URLs Guide](https://supabase.com/docs/guides/auth/redirect-urls)
- [Supabase Community Forum](https://github.com/supabase/supabase/discussions)

---

This guide provides a complete solution for customizing your Supabase email confirmation process, resulting in a more professional and branded user experience.

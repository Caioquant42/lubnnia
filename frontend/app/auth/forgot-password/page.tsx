"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { supabase } from "@/lib/supabase";
import Image from "next/image";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const { error: resetError } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      });
      
      if (resetError) throw resetError;
      
      setSuccess(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  if (success) {
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
              <h1 className="mt-3 text-3xl font-bold">E-mail enviado!</h1>
              <p className="mt-2 text-muted-foreground">
                Verifique sua caixa de entrada
              </p>
            </div>
            
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center space-y-4 text-center">
                  <div className="rounded-full bg-finance-success-500/10 p-3">
                    <Mail className="h-6 w-6 text-finance-success-500" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold">Instruções enviadas</h3>
                    <p className="text-sm text-muted-foreground">
                      Enviamos um link para redefinir sua senha para{" "}
                      <span className="font-medium">{email}</span>
                    </p>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <p>Verifique sua caixa de entrada e spam.</p>
                    <p>O link expira em 1 hora.</p>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <div className="w-full space-y-3">
                  <Button 
                    onClick={() => {
                      setSuccess(false);
                      setEmail("");
                    }}
                    variant="outline"
                    className="w-full"
                  >
                    Enviar outro e-mail
                  </Button>
                  <div className="text-center">
                    <Link
                      href="/auth/login"
                      className="text-sm text-finance-secondary-600 underline-offset-4 hover:underline"
                    >
                      Voltar para o login
                    </Link>
                  </div>
                </div>
              </CardFooter>
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
            <h1 className="mt-3 text-3xl font-bold">Esqueceu sua senha?</h1>
            <p className="mt-2 text-muted-foreground">
              Digite seu e-mail para receber um link de redefinição
            </p>
          </div>
          
          <Card>
            <form onSubmit={handleSubmit}>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {error && (
                    <div className="rounded-md bg-finance-danger-500/10 p-3 text-sm text-finance-danger-500">
                      {error}
                    </div>
                  )}
                  <div className="space-y-2">
                    <Label htmlFor="email">E-mail</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="nome@exemplo.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex flex-col gap-4">
                <Button 
                  type="submit" 
                  className="w-full bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500"
                  disabled={loading}
                >
                  {loading ? "Enviando..." : "Enviar link de redefinição"}
                </Button>
                <div className="text-center">
                  <Link
                    href="/auth/login"
                    className="text-sm text-finance-secondary-600 underline-offset-4 hover:underline flex items-center justify-center gap-2"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    Voltar para o login
                  </Link>
                </div>
              </CardFooter>
            </form>
          </Card>
          
          <div className="text-center text-sm">
            Não tem uma conta?{" "}
            <Link
              href="/auth/signup"
              className="text-finance-secondary-600 underline-offset-4 hover:underline"
            >
              Cadastrar-se
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

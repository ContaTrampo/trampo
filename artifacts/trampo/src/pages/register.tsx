import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useRegister } from "@workspace/api-client-react";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Target, User, Building } from "lucide-react";

const registerSchema = z.object({
  name: z.string().min(2, "Nome é obrigatório"),
  email: z.string().email("E-mail inválido"),
  password: z.string().min(6, "A senha deve ter pelo menos 6 caracteres"),
  role: z.enum(["candidate", "recruiter"]),
  cidade: z.string().optional(),
  estado: z.string().optional(),
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function Register() {
  const [, setLocation] = useLocation();
  const { login: authenticate } = useAuth();
  const { toast } = useToast();
  const registerMutation = useRegister();
  
  const form = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: { name: "", email: "", password: "", role: "candidate", cidade: "", estado: "" },
  });

  const selectedRole = form.watch("role");

  function onSubmit(data: RegisterForm) {
    registerMutation.mutate(
      { data },
      {
        onSuccess: (res) => {
          authenticate(res.token, res.user);
          toast({ title: "Conta criada!", description: "Bem-vindo ao TRAMPO." });
          if (res.user.role === 'recruiter') setLocation('/recrutador');
          else setLocation('/vagas');
        },
        onError: (err) => {
          toast({ title: "Erro no cadastro", description: err.message || "Ocorreu um erro.", variant: "destructive" });
        }
      }
    );
  }

  return (
    <div className="min-h-[90vh] flex flex-col items-center justify-center p-4 bg-muted/30 py-12">
      <div className="mb-8 flex flex-col items-center">
        <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center text-primary-foreground mb-4 shadow-lg">
          <Target className="w-7 h-7" />
        </div>
        <h1 className="text-3xl font-display font-bold text-foreground">Criar Conta</h1>
      </div>

      <Card className="w-full max-w-xl shadow-xl border-border/50">
        <CardHeader>
          <CardTitle>Cadastre-se no TRAMPO</CardTitle>
          <CardDescription>Preencha os dados abaixo para começar</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div 
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${selectedRole === 'candidate' ? 'border-primary bg-primary/5 shadow-sm' : 'border-border bg-card hover:border-primary/50'}`}
                  onClick={() => form.setValue("role", "candidate")}
                >
                  <User className={`w-8 h-8 mb-2 ${selectedRole === 'candidate' ? 'text-primary' : 'text-muted-foreground'}`} />
                  <h3 className="font-bold">Sou Candidato</h3>
                  <p className="text-xs text-muted-foreground mt-1">Quero buscar vagas e me candidatar</p>
                </div>
                <div 
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${selectedRole === 'recruiter' ? 'border-primary bg-primary/5 shadow-sm' : 'border-border bg-card hover:border-primary/50'}`}
                  onClick={() => form.setValue("role", "recruiter")}
                >
                  <Building className={`w-8 h-8 mb-2 ${selectedRole === 'recruiter' ? 'text-primary' : 'text-muted-foreground'}`} />
                  <h3 className="font-bold">Sou Empresa</h3>
                  <p className="text-xs text-muted-foreground mt-1">Quero publicar vagas e buscar talentos</p>
                </div>
              </div>

              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{selectedRole === 'recruiter' ? 'Nome da Empresa ou Recrutador' : 'Nome Completo'}</FormLabel>
                    <FormControl>
                      <Input placeholder="Digite o nome" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>E-mail corporativo ou pessoal</FormLabel>
                    <FormControl>
                      <Input placeholder="seu@email.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Senha</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="cidade"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Cidade (Opcional)</FormLabel>
                      <FormControl>
                        <Input placeholder="Ex: São Paulo" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="estado"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Estado (Opcional)</FormLabel>
                      <FormControl>
                        <Input placeholder="Ex: SP" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <Button type="submit" className="w-full h-12 text-md font-bold" disabled={registerMutation.isPending}>
                {registerMutation.isPending ? "Criando conta..." : "Criar Conta Grátis"}
              </Button>
            </form>
          </Form>
        </CardContent>
        <CardFooter className="flex justify-center border-t border-border/50 pt-6">
          <p className="text-sm text-muted-foreground">
            Já tem uma conta?{" "}
            <Link href="/login" className="text-primary font-bold hover:underline">
              Fazer login
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}

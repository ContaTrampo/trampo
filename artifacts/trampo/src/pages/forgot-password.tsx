import { useState } from "react";
import { Link } from "wouter";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useForgotPassword } from "@workspace/api-client-react";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { KeyRound } from "lucide-react";

const resetSchema = z.object({ email: z.string().email("E-mail inválido") });
type ResetForm = z.infer<typeof resetSchema>;

export default function ForgotPassword() {
  const { toast } = useToast();
  const resetMutation = useForgotPassword();
  const [sent, setSent] = useState(false);

  const form = useForm<ResetForm>({
    resolver: zodResolver(resetSchema),
    defaultValues: { email: "" },
  });

  function onSubmit(data: ResetForm) {
    resetMutation.mutate(
      { data },
      {
        onSuccess: () => {
          setSent(true);
          toast({ title: "E-mail enviado!", description: "Verifique sua caixa de entrada com as instruções." });
        },
        onError: () => {
          toast({ title: "Erro", description: "Não foi possível enviar o e-mail.", variant: "destructive" });
        }
      }
    );
  }

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center p-4 bg-muted/30">
      <Card className="w-full max-w-md shadow-xl border-border/50">
        <CardHeader className="text-center">
          <div className="w-12 h-12 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-4">
            <KeyRound className="w-6 h-6" />
          </div>
          <CardTitle className="text-2xl font-display">Recuperar Senha</CardTitle>
          <CardDescription>
            {sent ? "E-mail enviado com sucesso" : "Digite seu e-mail para receber um link de redefinição."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!sent ? (
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>E-mail</FormLabel>
                      <FormControl>
                        <Input placeholder="seu@email.com" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button type="submit" className="w-full font-bold" disabled={resetMutation.isPending}>
                  {resetMutation.isPending ? "Enviando..." : "Enviar Link"}
                </Button>
              </form>
            </Form>
          ) : (
            <div className="text-center p-6 bg-secondary/30 rounded-lg border border-border">
              <p className="text-sm font-medium mb-4">Caso o e-mail exista em nossa base, você receberá um link de recuperação em breve.</p>
              <Button asChild variant="outline" className="w-full">
                <Link href="/login">Voltar para o Login</Link>
              </Button>
            </div>
          )}
        </CardContent>
        {!sent && (
          <CardFooter className="flex justify-center border-t border-border/50 pt-6">
            <Link href="/login" className="text-sm text-primary font-bold hover:underline">
              Voltar para o Login
            </Link>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}

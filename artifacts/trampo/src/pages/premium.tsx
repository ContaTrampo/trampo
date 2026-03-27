import { useGetPaymentStatus, useCreateCheckout } from "@workspace/api-client-react";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Zap, Star, Loader2 } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function Premium() {
  const { user } = useAuth();
  const { data: status, isLoading } = useGetPaymentStatus();
  const checkout = useCreateCheckout();

  const handleSubscribe = () => {
    checkout.mutate(undefined, {
      onSuccess: (data) => {
        window.location.href = data.checkout_url;
      }
    });
  };

  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

  return (
    <div className="container max-w-5xl py-16 mx-auto px-4">
      <div className="text-center max-w-2xl mx-auto mb-16">
        <div className="inline-flex items-center justify-center p-3 bg-accent/20 text-accent-foreground rounded-full mb-6">
          <Zap className="w-8 h-8 text-accent" />
        </div>
        <h1 className="text-4xl md:text-5xl font-display font-extrabold text-foreground mb-4">
          TRAMPO <span className="text-accent">Premium</span>
        </h1>
        <p className="text-lg text-muted-foreground">
          Maximize suas chances. Use a IA sem limites e tenha destaque nas buscas dos recrutadores.
        </p>
      </div>

      {status?.is_premium ? (
        <div className="max-w-xl mx-auto bg-gradient-to-br from-primary to-primary/80 rounded-3xl p-8 text-primary-foreground shadow-2xl text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
          <Star className="w-16 h-16 text-accent mx-auto mb-6 relative z-10" fill="currentColor" />
          <h2 className="text-3xl font-display font-bold mb-2 relative z-10">Você já é Premium!</h2>
          <p className="text-primary-foreground/80 mb-6 relative z-10">Aproveite todos os benefícios ilimitados da plataforma.</p>
          <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm inline-block relative z-10">
            Validade: <span className="font-bold">{status.premium_expires_at ? format(new Date(status.premium_expires_at), "dd 'de' MMMM 'de' yyyy", { locale: ptBR }) : 'Vitalício'}</span>
          </div>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8 items-center">
          <div className="space-y-6">
            <h3 className="text-2xl font-bold">Por que assinar?</h3>
            <ul className="space-y-4">
              {[
                "Candidaturas Ilimitadas por dia",
                "Selo de Perfil Destaque para os Recrutadores",
                "Feedback detalhado da IA sobre por que você não passou",
                "Acesso antecipado a vagas remotas",
                "Suporte prioritário"
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3">
                  <CheckCircle2 className="w-6 h-6 text-primary shrink-0" />
                  <span className="text-muted-foreground font-medium">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-card rounded-3xl border border-border shadow-2xl p-8 text-center relative overflow-hidden group hover:border-accent transition-colors">
            <div className="absolute top-0 right-0 p-4">
              <span className="bg-accent text-accent-foreground text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">Mais Popular</span>
            </div>
            
            <h3 className="text-xl font-display font-bold text-muted-foreground mb-4 pt-4">Plano Mensal</h3>
            <div className="flex justify-center items-end gap-1 mb-8">
              <span className="text-2xl font-bold text-foreground">R$</span>
              <span className="text-6xl font-display font-extrabold text-foreground">29</span>
              <span className="text-muted-foreground font-medium mb-2">/mês</span>
            </div>
            
            <Button 
              size="lg" 
              className="w-full h-14 text-lg font-bold bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg hover:shadow-xl transition-all hover-elevate"
              onClick={handleSubscribe}
              disabled={checkout.isPending}
            >
              {checkout.isPending ? "Gerando Checkout..." : "Assinar Agora"}
            </Button>
            <p className="text-xs text-muted-foreground mt-4">Cancele quando quiser. Pagamento seguro via Stripe.</p>
          </div>
        </div>
      )}
    </div>
  );
}

import { motion } from "framer-motion";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Star, TrendingUp, Users, Target, Zap } from "lucide-react";
import { useAuth } from "@/lib/auth";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="flex flex-col w-full">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden bg-foreground">
        <div className="absolute inset-0 z-0">
          <img 
            src={`${import.meta.env.BASE_URL}images/hero-bg.png`} 
            alt="Hero Background" 
            className="w-full h-full object-cover opacity-30 mix-blend-overlay" 
          />
          <div className="absolute inset-0 bg-gradient-to-t from-foreground via-foreground/80 to-transparent" />
        </div>
        
        <div className="container relative z-10 mx-auto px-4 text-center max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 border border-accent/20 text-accent mb-8">
              <Zap className="w-4 h-4" />
              <span className="text-sm font-semibold tracking-wide">IA para sua carreira</span>
            </div>
            
            <h1 className="text-5xl lg:text-7xl font-display font-extrabold text-white leading-tight mb-6">
              Encontre o <span className="text-accent">trampo certo</span> mais rápido com IA.
            </h1>
            
            <p className="text-lg lg:text-xl text-zinc-300 mb-10 max-w-2xl mx-auto">
              A primeira plataforma do Brasil que lê seu currículo, faz o match perfeito com empresas e automatiza suas candidaturas.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button asChild size="lg" className="h-14 px-8 text-lg font-bold rounded-xl bg-accent text-accent-foreground hover:bg-accent/90 shadow-[0_0_40px_rgba(255,184,0,0.3)]">
                <Link href={user ? "/vagas" : "/cadastro"}>
                  {user ? "Buscar Vagas" : "Criar Conta Grátis"}
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="h-14 px-8 text-lg font-bold rounded-xl border-zinc-700 text-white hover:bg-zinc-800 hover:text-white bg-transparent">
                <Link href="/cadastro">Sou uma Empresa</Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Strip */}
      <section className="border-y border-border/50 bg-background py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap justify-center gap-12 md:gap-24 text-center">
            <div className="space-y-2">
              <h3 className="text-4xl font-display font-bold text-primary">10k+</h3>
              <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">Vagas Ativas</p>
            </div>
            <div className="space-y-2">
              <h3 className="text-4xl font-display font-bold text-primary">92%</h3>
              <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">Taxa de Match</p>
            </div>
            <div className="space-y-2">
              <h3 className="text-4xl font-display font-bold text-primary">5k+</h3>
              <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">Empresas</p>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Mockup Section */}
      <section className="py-24 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="max-w-5xl mx-auto relative"
          >
            <div className="absolute inset-0 bg-primary/10 blur-[100px] rounded-full -z-10" />
            <img 
              src={`${import.meta.env.BASE_URL}images/app-mockup.png`} 
              alt="Plataforma TRAMPO" 
              className="mx-auto rounded-2xl shadow-2xl shadow-primary/20 border border-border/50 w-full"
            />
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 bg-background">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-display font-bold text-foreground mb-4">
              Por que usar o TRAMPO?
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Nossa IA faz o trabalho duro para você focar no que importa: a entrevista.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-card p-8 rounded-2xl border border-border shadow-sm hover:shadow-lg transition-all duration-300 group">
              <div className="w-14 h-14 bg-primary/10 rounded-xl flex items-center justify-center mb-6 group-hover:-translate-y-1 transition-transform">
                <Target className="w-7 h-7 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Match Perfeito</h3>
              <p className="text-muted-foreground leading-relaxed">
                Nossa IA cruza suas habilidades com as vagas e mostra a % de compatibilidade real antes mesmo de você se candidatar.
              </p>
            </div>

            <div className="bg-card p-8 rounded-2xl border border-border shadow-sm hover:shadow-lg transition-all duration-300 group">
              <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mb-6 group-hover:-translate-y-1 transition-transform">
                <Zap className="w-7 h-7 text-accent" />
              </div>
              <h3 className="text-xl font-bold mb-3">Candidatura em 1 Clique</h3>
              <p className="text-muted-foreground leading-relaxed">
                Chega de preencher as mesmas informações dezenas de vezes. Seu perfil TRAMPO é o seu passe livre para qualquer vaga.
              </p>
            </div>

            <div className="bg-card p-8 rounded-2xl border border-border shadow-sm hover:shadow-lg transition-all duration-300 group">
              <div className="w-14 h-14 bg-blue-500/10 rounded-xl flex items-center justify-center mb-6 group-hover:-translate-y-1 transition-transform">
                <TrendingUp className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold mb-3">Feedback Real</h3>
              <p className="text-muted-foreground leading-relaxed">
                Acompanhe o status de cada candidatura em tempo real. Saiba se seu currículo foi visto e receba respostas de verdade.
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* CTA */}
      <section className="py-24 bg-primary text-primary-foreground relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white via-transparent to-transparent" />
        <div className="container mx-auto px-4 text-center relative z-10">
          <h2 className="text-4xl font-display font-bold mb-6">Pronto para o próximo nível?</h2>
          <p className="text-lg text-primary-foreground/80 mb-10 max-w-2xl mx-auto">
            Junte-se a milhares de brasileiros que já encontraram o emprego dos sonhos usando o TRAMPO.
          </p>
          <Button asChild size="lg" className="h-14 px-10 text-lg font-bold rounded-xl bg-accent text-accent-foreground hover:bg-accent/90 shadow-xl shadow-black/20">
            <Link href="/cadastro">Começar Agora Gratuitamente</Link>
          </Button>
        </div>
      </section>
    </div>
  );
}

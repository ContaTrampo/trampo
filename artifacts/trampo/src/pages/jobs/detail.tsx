import { useParams, useLocation, Link } from "wouter";
import { useGetJob, useCreateApplication } from "@workspace/api-client-react";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { MapPin, Briefcase, DollarSign, Clock, Building, ArrowLeft, CheckCircle2 } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function JobDetail() {
  const params = useParams();
  const id = parseInt(params.id || "0");
  const [, setLocation] = useLocation();
  const { user } = useAuth();
  const { toast } = useToast();
  
  const { data: job, isLoading, isError } = useGetJob(id);
  const createApplication = useCreateApplication();

  const handleApply = () => {
    if (!user) {
      toast({ title: "Atenção", description: "Você precisa fazer login para se candidatar." });
      setLocation("/login");
      return;
    }
    
    if (user.role !== 'candidate') {
      toast({ title: "Atenção", description: "Apenas candidatos podem se inscrever em vagas.", variant: "destructive" });
      return;
    }

    createApplication.mutate(
      { data: { job_id: id } },
      {
        onSuccess: () => {
          toast({ 
            title: "Candidatura enviada!", 
            description: "Você se candidatou a esta vaga com sucesso. Boa sorte!",
          });
          setLocation("/minhas-candidaturas");
        },
        onError: (err) => {
          toast({ title: "Erro na candidatura", description: err.message || "Tente novamente.", variant: "destructive" });
        }
      }
    );
  };

  if (isLoading) return (
    <div className="container max-w-4xl mx-auto py-12 px-4 space-y-6">
      <Skeleton className="h-8 w-24 mb-8" />
      <Skeleton className="h-12 w-3/4" />
      <Skeleton className="h-6 w-1/2" />
      <Skeleton className="h-64 w-full mt-8" />
    </div>
  );

  if (isError || !job) return (
    <div className="container max-w-4xl mx-auto py-24 text-center">
      <h2 className="text-2xl font-bold text-destructive mb-4">Vaga não encontrada</h2>
      <Button variant="outline" onClick={() => setLocation("/vagas")}>Voltar para Vagas</Button>
    </div>
  );

  return (
    <div className="bg-muted/10 min-h-screen pb-20">
      {/* Header */}
      <div className="bg-card border-b border-border pt-8 pb-12 shadow-sm">
        <div className="container max-w-4xl mx-auto px-4">
          <Button variant="ghost" className="mb-6 -ml-4 text-muted-foreground hover:text-primary" onClick={() => setLocation("/vagas")}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Voltar para Vagas
          </Button>
          
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
            <div className="space-y-4 flex-1">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                  <Building className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-3xl md:text-4xl font-display font-bold text-foreground">{job.title}</h1>
                  <p className="text-xl text-primary font-medium">{job.company}</p>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-4 text-sm font-medium text-muted-foreground pt-2">
                <div className="flex items-center gap-1.5 bg-secondary/50 px-3 py-1.5 rounded-md">
                  <MapPin className="w-4 h-4 text-primary" />
                  {job.cidade ? `${job.cidade} - ${job.estado}` : "Remoto"}
                </div>
                <div className="flex items-center gap-1.5 bg-secondary/50 px-3 py-1.5 rounded-md">
                  <Briefcase className="w-4 h-4 text-primary" />
                  <span className="capitalize">{job.contract_type} • {job.work_mode}</span>
                </div>
                {(job.salary_min || job.salary_max) && (
                  <div className="flex items-center gap-1.5 bg-secondary/50 px-3 py-1.5 rounded-md">
                    <DollarSign className="w-4 h-4 text-primary" />
                    <span>
                      {job.salary_min ? `R$ ${job.salary_min.toLocaleString('pt-BR')}` : ""} 
                      {job.salary_min && job.salary_max ? " - " : ""} 
                      {job.salary_max ? `R$ ${job.salary_max.toLocaleString('pt-BR')}` : ""}
                    </span>
                  </div>
                )}
                <div className="flex items-center gap-1.5 bg-secondary/50 px-3 py-1.5 rounded-md">
                  <Clock className="w-4 h-4 text-primary" />
                  Publicada em {format(new Date(job.posted_at), "dd/MM/yyyy", { locale: ptBR })}
                </div>
              </div>
            </div>
            
            <div className="w-full md:w-auto shrink-0 flex flex-col gap-3">
              <Button 
                size="lg" 
                className="w-full md:w-64 font-bold text-lg h-14 bg-accent text-accent-foreground hover:bg-accent/90 shadow-lg hover:shadow-xl transition-all"
                onClick={handleApply}
                disabled={createApplication.isPending || job.status === 'closed'}
              >
                {createApplication.isPending ? "Enviando..." : job.status === 'closed' ? "Vaga Fechada" : "Candidatar-se"}
              </Button>
              {user?.role === 'candidate' && (
                <div className="text-center flex justify-center text-sm font-medium text-emerald-600 bg-emerald-50 py-2 rounded-lg border border-emerald-100">
                  <CheckCircle2 className="w-4 h-4 mr-1.5" /> IA TRAMPO Match Ativado
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container max-w-4xl mx-auto px-4 mt-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-8">
          <section className="bg-card p-6 rounded-2xl border border-border shadow-sm">
            <h3 className="text-xl font-display font-bold mb-4 flex items-center gap-2">
              Descrição da Vaga
            </h3>
            <div className="prose prose-zinc dark:prose-invert max-w-none text-muted-foreground whitespace-pre-wrap leading-relaxed">
              {job.description}
            </div>
          </section>

          {job.benefits && (
            <section className="bg-card p-6 rounded-2xl border border-border shadow-sm">
              <h3 className="text-xl font-display font-bold mb-4">Benefícios</h3>
              <div className="prose prose-zinc dark:prose-invert max-w-none text-muted-foreground whitespace-pre-wrap leading-relaxed">
                {job.benefits}
              </div>
            </section>
          )}
        </div>

        <div className="space-y-6">
          <section className="bg-card p-6 rounded-2xl border border-border shadow-sm">
            <h3 className="font-bold text-lg mb-4">Requisitos</h3>
            
            {job.required_experience && (
              <div className="mb-4 pb-4 border-b border-border">
                <p className="text-sm text-muted-foreground">Experiência Mínima</p>
                <p className="font-semibold">{job.required_experience} anos</p>
              </div>
            )}
            
            <div>
              <p className="text-sm text-muted-foreground mb-3">Habilidades Técnicas</p>
              <div className="flex flex-wrap gap-2">
                {job.required_skills ? job.required_skills.split(',').map((skill, i) => (
                  <Badge key={i} variant="secondary" className="bg-secondary text-secondary-foreground font-medium py-1 px-3">
                    {skill.trim()}
                  </Badge>
                )) : (
                  <span className="text-sm italic">Não especificadas</span>
                )}
              </div>
            </div>
          </section>

          <section className="bg-primary text-primary-foreground p-6 rounded-2xl shadow-lg relative overflow-hidden">
            <div className="absolute top-0 right-0 -mr-4 -mt-4 w-24 h-24 bg-accent/20 rounded-full blur-xl"></div>
            <h3 className="font-bold text-lg mb-2 relative z-10">Dica do TRAMPO</h3>
            <p className="text-sm text-primary-foreground/80 leading-relaxed relative z-10">
              Certifique-se de que seu perfil está 100% preenchido. Nossa IA cruza as palavras-chave do seu currículo com as habilidades requeridas pela vaga.
            </p>
            <Button asChild variant="outline" className="mt-4 w-full bg-transparent border-primary-foreground/30 hover:bg-primary-foreground/10 text-primary-foreground">
              <Link href="/perfil">Atualizar Perfil</Link>
            </Button>
          </section>
        </div>
      </div>
    </div>
  );
}

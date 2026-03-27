import { useGetCandidateApplications } from "@workspace/api-client-react";
import { Link } from "wouter";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Building, MapPin, Loader2, ArrowRight } from "lucide-react";

export default function Applications() {
  const { data: applications, isLoading } = useGetCandidateApplications();

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'sent': return 'bg-zinc-100 text-zinc-700 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-300';
      case 'viewed': return 'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400';
      case 'responded': return 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400';
      case 'rejected': return 'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400';
      default: return 'bg-secondary text-secondary-foreground';
    }
  };

  const getStatusText = (status: string) => {
    switch(status) {
      case 'sent': return 'Enviada';
      case 'viewed': return 'Visualizada';
      case 'responded': return 'Em Processo';
      case 'rejected': return 'Recusada';
      default: return status;
    }
  };

  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

  return (
    <div className="container max-w-5xl py-12 mx-auto px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold text-foreground">Minhas Candidaturas</h1>
          <p className="text-muted-foreground mt-1">Acompanhe o status dos seus processos seletivos.</p>
        </div>
        <Button asChild className="bg-primary text-primary-foreground">
          <Link href="/vagas">Explorar Mais Vagas</Link>
        </Button>
      </div>

      {applications && applications.length === 0 ? (
        <Card className="py-20 text-center border-dashed border-2 bg-muted/20">
          <div className="max-w-sm mx-auto">
            <h3 className="text-xl font-bold mb-2">Você ainda não se candidatou</h3>
            <p className="text-muted-foreground mb-6">Comece agora mesmo a buscar as melhores oportunidades que dão match com o seu perfil.</p>
            <Button asChild>
              <Link href="/vagas">Ver Vagas Disponíveis</Link>
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {applications?.map((app) => (
            <Card key={app.id} className="hover-elevate transition-all border-border/60">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                  
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                      <Building className="w-6 h-6 text-muted-foreground" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-foreground leading-tight mb-1">{app.job?.title}</h3>
                      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground font-medium">
                        <span className="text-primary">{app.job?.company}</span>
                        <span className="w-1 h-1 rounded-full bg-border"></span>
                        <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {app.job?.cidade || "Remoto"}</span>
                        <span className="w-1 h-1 rounded-full bg-border"></span>
                        <span>{format(new Date(app.sent_at), "dd/MM/yyyy", { locale: ptBR })}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-row md:flex-col items-center md:items-end justify-between w-full md:w-48 shrink-0 gap-4">
                    <Badge variant="outline" className={`px-3 py-1 text-sm border font-bold ${getStatusColor(app.status)}`}>
                      {getStatusText(app.status)}
                    </Badge>
                    
                    <div className="flex items-center gap-3 w-full max-w-[150px]">
                      <div className="flex-1">
                        <div className="flex justify-between text-xs mb-1 font-bold">
                          <span className="text-muted-foreground">Match IA</span>
                          <span className={app.match_score && app.match_score > 80 ? "text-emerald-600 dark:text-emerald-400" : "text-primary"}>
                            {app.match_score || 0}%
                          </span>
                        </div>
                        <Progress value={app.match_score || 0} className="h-2" />
                      </div>
                    </div>
                  </div>

                  <div className="hidden md:block">
                    <Button variant="ghost" size="icon" asChild className="text-muted-foreground hover:text-primary">
                      <Link href={`/vaga/${app.job_id}`}><ArrowRight className="w-5 h-5" /></Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

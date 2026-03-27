import { Job } from "@workspace/api-client-react";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Link } from "wouter";
import { MapPin, Briefcase, DollarSign, Clock } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export function JobCard({ job }: { job: Job }) {
  return (
    <Card className="hover-elevate transition-all duration-300 flex flex-col h-full border-border/50 shadow-sm hover:shadow-md">
      <CardHeader className="pb-4">
        <div className="flex justify-between items-start gap-4">
          <div className="space-y-1">
            <CardTitle className="text-xl font-display text-primary leading-tight line-clamp-2">
              {job.title}
            </CardTitle>
            <p className="text-muted-foreground font-medium text-sm">{job.company}</p>
          </div>
          {job.is_featured && (
            <Badge className="bg-accent text-accent-foreground border-none font-semibold shrink-0">
              Destaque
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="pb-6 flex-1 space-y-3">
        <div className="space-y-2 text-sm text-muted-foreground font-medium">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 shrink-0 text-primary/60" />
            <span className="truncate">{job.cidade ? `${job.cidade} - ${job.estado}` : "Remoto"}</span>
          </div>
          
          <div className="flex items-center gap-2">
            <Briefcase className="w-4 h-4 shrink-0 text-primary/60" />
            <span className="capitalize">{job.contract_type} • {job.work_mode}</span>
          </div>
          
          {(job.salary_min || job.salary_max) && (
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 shrink-0 text-primary/60" />
              <span>
                {job.salary_min ? `R$ ${job.salary_min.toLocaleString('pt-BR')}` : ""} 
                {job.salary_min && job.salary_max ? " - " : ""} 
                {job.salary_max ? `R$ ${job.salary_max.toLocaleString('pt-BR')}` : ""}
              </span>
            </div>
          )}

          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 shrink-0 text-primary/60" />
            <span>Postada em {format(new Date(job.posted_at), "dd 'de' MMM", { locale: ptBR })}</span>
          </div>
        </div>

        {job.required_skills && (
          <div className="flex flex-wrap gap-2 mt-4">
            {job.required_skills.split(',').slice(0, 3).map((skill, i) => (
              <Badge key={i} variant="secondary" className="bg-secondary text-secondary-foreground font-medium">
                {skill.trim()}
              </Badge>
            ))}
            {job.required_skills.split(',').length > 3 && (
              <Badge variant="secondary" className="bg-secondary text-secondary-foreground">
                +{job.required_skills.split(',').length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardContent>
      
      <CardFooter className="pt-0 mt-auto">
        <Button asChild className="w-full" variant="outline">
          <Link href={`/vaga/${job.id}`}>Ver Detalhes da Vaga</Link>
        </Button>
      </CardFooter>
    </Card>
  );
}

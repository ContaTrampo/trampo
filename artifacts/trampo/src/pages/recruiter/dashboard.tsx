import { useState } from "react";
import { Link } from "wouter";
import { useGetRecruiterJobs, useCreateJob, CreateJobRequestWorkMode, CreateJobRequestContractType } from "@workspace/api-client-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Briefcase, Users, Plus, Loader2, ArrowRight } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

const createJobSchema = z.object({
  title: z.string().min(3, "Obrigatório"),
  company: z.string().min(2, "Obrigatório"),
  description: z.string().min(10, "Detalhe mais a vaga"),
  location: z.string().optional(),
  cidade: z.string().optional(),
  estado: z.string().optional(),
  contract_type: z.enum(["clt", "pj", "freelancer", "internship"]),
  salary_min: z.coerce.number().optional(),
  salary_max: z.coerce.number().optional(),
  work_mode: z.enum(["remote", "hybrid", "onsite"]),
  required_skills: z.string().optional(),
  required_experience: z.coerce.number().optional(),
  contact_email: z.string().email(),
  benefits: z.string().optional(),
});

type CreateJobForm = z.infer<typeof createJobSchema>;

export default function RecruiterDashboard() {
  const { data: jobs, isLoading } = useGetRecruiterJobs();
  const createJob = useCreateJob();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);

  const form = useForm<CreateJobForm>({
    resolver: zodResolver(createJobSchema),
    defaultValues: {
      title: "", company: "", description: "", cidade: "", estado: "",
      contract_type: "clt", work_mode: "remote", contact_email: "",
      required_skills: "", salary_min: undefined, salary_max: undefined, required_experience: undefined
    }
  });

  const onSubmit = (data: CreateJobForm) => {
    createJob.mutate(
      { data: data as any },
      {
        onSuccess: () => {
          toast({ title: "Sucesso", description: "Vaga publicada com sucesso!" });
          setOpen(false);
          form.reset();
        },
        onError: (err) => {
          toast({ title: "Erro", description: err.message, variant: "destructive" });
        }
      }
    );
  };

  const activeJobs = jobs?.filter(j => j.status === 'active') || [];
  
  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

  return (
    <div className="container max-w-6xl py-12 mx-auto px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-10">
        <div>
          <h1 className="text-3xl font-display font-bold text-foreground">Painel da Empresa</h1>
          <p className="text-muted-foreground mt-1">Gerencie suas vagas e visualize candidatos.</p>
        </div>
        
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-accent text-accent-foreground font-bold shadow-md hover:bg-accent/90 px-6">
              <Plus className="w-4 h-4 mr-2" /> Publicar Nova Vaga
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-2xl font-display">Publicar Nova Vaga</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField control={form.control} name="title" render={({ field }) => (
                    <FormItem className="col-span-2 md:col-span-1">
                      <FormLabel>Título da Vaga</FormLabel>
                      <FormControl><Input placeholder="Ex: Desenvolvedor Senior" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="company" render={({ field }) => (
                    <FormItem className="col-span-2 md:col-span-1">
                      <FormLabel>Nome da Empresa</FormLabel>
                      <FormControl><Input placeholder="Sua Empresa Tech" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField control={form.control} name="cidade" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Cidade</FormLabel>
                      <FormControl><Input placeholder="São Paulo" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="estado" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Estado (UF)</FormLabel>
                      <FormControl><Input placeholder="SP" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField control={form.control} name="work_mode" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Modalidade</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                        <SelectContent>
                          <SelectItem value="remote">Remoto</SelectItem>
                          <SelectItem value="hybrid">Híbrido</SelectItem>
                          <SelectItem value="onsite">Presencial</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="contract_type" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contrato</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                        <SelectContent>
                          <SelectItem value="clt">CLT</SelectItem>
                          <SelectItem value="pj">PJ</SelectItem>
                          <SelectItem value="freelancer">Freelancer</SelectItem>
                          <SelectItem value="internship">Estágio</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>

                <FormField control={form.control} name="required_skills" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Habilidades Requeridas (Crucial para a IA)</FormLabel>
                    <FormControl><Input placeholder="React, Node.js, AWS (separadas por vírgula)" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />

                <FormField control={form.control} name="description" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Descrição Detalhada</FormLabel>
                    <FormControl><Textarea className="h-32 resize-none" placeholder="Descreva as responsabilidades..." {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />

                <FormField control={form.control} name="contact_email" render={({ field }) => (
                  <FormItem>
                    <FormLabel>E-mail de Contato/Retorno</FormLabel>
                    <FormControl><Input placeholder="vagas@empresa.com" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />

                <Button type="submit" className="w-full mt-4" disabled={createJob.isPending}>
                  {createJob.isPending ? "Publicando..." : "Publicar Vaga"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <Card className="bg-primary text-primary-foreground border-none shadow-lg">
          <CardContent className="p-6 flex items-center justify-between">
            <div>
              <p className="text-primary-foreground/80 text-sm font-medium mb-1">Vagas Ativas</p>
              <h2 className="text-4xl font-display font-bold">{activeJobs.length}</h2>
            </div>
            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <Briefcase className="w-6 h-6 text-white" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border shadow-sm">
          <CardContent className="p-6 flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm font-medium mb-1">Total de Candidaturas</p>
              {/* Note: Needs aggregate endpoint in real life, using a placeholder logic here */}
              <h2 className="text-4xl font-display font-bold text-foreground">--</h2>
            </div>
            <div className="w-12 h-12 bg-secondary rounded-full flex items-center justify-center">
              <Users className="w-6 h-6 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      <h2 className="text-xl font-bold mb-6">Suas Vagas Publicadas</h2>
      
      {jobs && jobs.length === 0 ? (
        <div className="text-center py-16 bg-muted/30 rounded-xl border border-dashed border-border">
          <Briefcase className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-bold mb-2">Nenhuma vaga publicada</h3>
          <p className="text-muted-foreground">Publique sua primeira oportunidade e deixe a IA encontrar os melhores talentos.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs?.map((job) => (
            <Card key={job.id} className="border-border shadow-sm hover:shadow-md transition-shadow">
              <div className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-bold text-primary">{job.title}</h3>
                    <div className={`px-2 py-0.5 rounded text-xs font-bold ${job.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-zinc-100 text-zinc-600'}`}>
                      {job.status === 'active' ? 'Ativa' : 'Fechada'}
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground flex gap-4">
                    <span>{job.work_mode}</span>
                    <span>{format(new Date(job.posted_at), "dd/MM/yyyy", { locale: ptBR })}</span>
                  </div>
                </div>
                
                <Button variant="outline" className="shrink-0" asChild>
                  <Link href={`/vaga/${job.id}`}>Ver Detalhes <ArrowRight className="w-4 h-4 ml-2" /></Link>
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

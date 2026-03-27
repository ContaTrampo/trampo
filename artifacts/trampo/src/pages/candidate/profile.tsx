import { useEffect } from "react";
import { useGetCandidateProfile, useUpdateCandidateProfile, UpdateCandidateProfileRequestWorkMode, UpdateCandidateProfileRequestSeniority, UpdateCandidateProfileRequestAvailability } from "@workspace/api-client-react";
import { useUploadResume, useUploadPhoto } from "@/hooks/use-uploads";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { User, FileText, UploadCloud, Loader2 } from "lucide-react";

const profileSchema = z.object({
  job_title: z.string().optional(),
  years_experience: z.coerce.number().optional(),
  seniority: z.enum(["junior", "mid", "senior", "lead"]).optional(),
  salary_min: z.coerce.number().optional(),
  work_mode: z.enum(["remote", "hybrid", "onsite", "any"]).optional(),
  availability: z.enum(["immediate", "2weeks", "1month"]).optional(),
  bio: z.string().optional(),
  skills: z.string().optional(),
  linkedin_url: z.string().url().or(z.literal("")).optional(),
  github_url: z.string().url().or(z.literal("")).optional(),
  location: z.string().optional(),
});

type ProfileForm = z.infer<typeof profileSchema>;

export default function Profile() {
  const { toast } = useToast();
  const { data: profile, isLoading } = useGetCandidateProfile();
  const updateProfile = useUpdateCandidateProfile();
  const uploadResume = useUploadResume();
  const uploadPhoto = useUploadPhoto();

  const form = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      job_title: "",
      years_experience: 0,
      bio: "",
      skills: "",
      linkedin_url: "",
      github_url: "",
      location: "",
    }
  });

  useEffect(() => {
    if (profile) {
      form.reset({
        job_title: profile.job_title || "",
        years_experience: profile.years_experience || 0,
        seniority: profile.seniority as any,
        salary_min: profile.salary_min || undefined,
        work_mode: profile.work_mode as any,
        availability: profile.availability as any,
        bio: profile.bio || "",
        skills: profile.skills || "",
        linkedin_url: profile.linkedin_url || "",
        github_url: profile.github_url || "",
        location: profile.location || "",
      });
    }
  }, [profile, form]);

  const onSubmit = (data: ProfileForm) => {
    updateProfile.mutate(
      { data: data as any },
      {
        onSuccess: () => {
          toast({ title: "Sucesso", description: "Perfil atualizado com sucesso!" });
        },
        onError: (err) => {
          toast({ title: "Erro", description: err.message || "Erro ao salvar perfil", variant: "destructive" });
        }
      }
    );
  };

  const handleResumeUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadResume.mutate(file);
    }
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadPhoto.mutate(file);
    }
  };

  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

  return (
    <div className="container max-w-5xl py-12 mx-auto px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-foreground">Meu Perfil TRAMPO</h1>
        <p className="text-muted-foreground mt-1">Complete seu perfil para que nossa IA te conecte às melhores vagas.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-1 space-y-6">
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2"><User className="w-5 h-5 text-primary" /> Foto de Perfil</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center text-center">
              <div className="w-32 h-32 rounded-full bg-secondary border-4 border-background shadow-lg overflow-hidden flex items-center justify-center mb-4">
                {profile?.photo_url ? (
                  <img src={profile.photo_url} alt="Profile" className="w-full h-full object-cover" />
                ) : (
                  <User className="w-12 h-12 text-muted-foreground" />
                )}
              </div>
              <Button variant="outline" className="relative cursor-pointer" disabled={uploadPhoto.isPending}>
                <input type="file" accept="image/*" onChange={handlePhotoUpload} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                {uploadPhoto.isPending ? "Enviando..." : "Alterar Foto"}
              </Button>
            </CardContent>
          </Card>

          <Card className="shadow-sm border-accent/20 bg-accent/5">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2"><FileText className="w-5 h-5 text-accent" /> Currículo para IA</CardTitle>
              <CardDescription>A IA extrai suas habilidades automaticamente do PDF.</CardDescription>
            </CardHeader>
            <CardContent>
              {profile?.resume_filename && (
                <div className="mb-4 p-3 bg-card border border-border rounded-lg text-sm truncate flex items-center gap-2">
                  <FileText className="w-4 h-4 text-primary shrink-0" />
                  {profile.resume_filename}
                </div>
              )}
              <Button className="w-full relative overflow-hidden bg-primary text-primary-foreground hover:bg-primary/90" disabled={uploadResume.isPending}>
                <input type="file" accept=".pdf,.doc,.docx" onChange={handleResumeUpload} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                <UploadCloud className="w-4 h-4 mr-2" />
                {uploadResume.isPending ? "Processando..." : profile?.resume_filename ? "Atualizar Currículo" : "Fazer Upload (PDF)"}
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2">
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle>Informações Profissionais</CardTitle>
              <CardDescription>Esses dados aumentam seu match com as empresas.</CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="job_title"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Cargo Atual ou Desejado</FormLabel>
                          <FormControl><Input placeholder="Ex: Desenvolvedor Front-end" {...field} /></FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="location"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Localização (Cidade/Estado)</FormLabel>
                          <FormControl><Input placeholder="Ex: São Paulo, SP" {...field} /></FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="seniority"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Senioridade</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl><SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger></FormControl>
                            <SelectContent>
                              <SelectItem value="junior">Júnior</SelectItem>
                              <SelectItem value="mid">Pleno</SelectItem>
                              <SelectItem value="senior">Sênior</SelectItem>
                              <SelectItem value="lead">Lead/Especialista</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="years_experience"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Anos de Experiência</FormLabel>
                          <FormControl><Input type="number" {...field} /></FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="salary_min"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Pretensão Salarial (Min)</FormLabel>
                          <FormControl><Input type="number" placeholder="Ex: 5000" {...field} /></FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="work_mode"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Modalidade de Trabalho</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl><SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger></FormControl>
                            <SelectContent>
                              <SelectItem value="any">Qualquer</SelectItem>
                              <SelectItem value="remote">Remoto</SelectItem>
                              <SelectItem value="hybrid">Híbrido</SelectItem>
                              <SelectItem value="onsite">Presencial</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="availability"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Disponibilidade</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl><SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger></FormControl>
                            <SelectContent>
                              <SelectItem value="immediate">Imediata</SelectItem>
                              <SelectItem value="2weeks">15 dias</SelectItem>
                              <SelectItem value="1month">30 dias</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="skills"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Habilidades Principais (Separadas por vírgula)</FormLabel>
                        <FormControl><Input placeholder="React, Node.js, TypeScript, UI/UX" {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="bio"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Resumo Profissional (Bio)</FormLabel>
                        <FormControl><Textarea className="h-24 resize-none" placeholder="Fale um pouco sobre você, sua trajetória e seus objetivos..." {...field} /></FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="linkedin_url"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>LinkedIn URL</FormLabel>
                          <FormControl><Input placeholder="https://linkedin.com/in/..." {...field} /></FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="github_url"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>GitHub / Portfólio URL</FormLabel>
                          <FormControl><Input placeholder="https://github.com/..." {...field} /></FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="flex justify-end pt-4 border-t border-border">
                    <Button type="submit" size="lg" className="font-bold px-8" disabled={updateProfile.isPending}>
                      {updateProfile.isPending ? "Salvando..." : "Salvar Perfil"}
                    </Button>
                  </div>
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

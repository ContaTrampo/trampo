import { useListSupportTickets, useCreateSupportTicket } from "@workspace/api-client-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Ticket, Clock, CheckCircle2 } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

const ticketSchema = z.object({
  subject: z.string().min(5, "Assunto muito curto"),
  message: z.string().min(20, "Mensagem muito curta, detalhe melhor seu problema"),
});

type TicketForm = z.infer<typeof ticketSchema>;

export default function Support() {
  const { data: tickets, refetch } = useListSupportTickets();
  const createTicket = useCreateSupportTicket();
  const { toast } = useToast();

  const form = useForm<TicketForm>({
    resolver: zodResolver(ticketSchema),
    defaultValues: { subject: "", message: "" }
  });

  const onSubmit = (data: TicketForm) => {
    createTicket.mutate(
      { data },
      {
        onSuccess: () => {
          toast({ title: "Ticket Aberto", description: "Responderemos o mais rápido possível." });
          form.reset();
          refetch();
        },
        onError: () => {
          toast({ title: "Erro", description: "Falha ao enviar ticket.", variant: "destructive" });
        }
      }
    );
  };

  return (
    <div className="container max-w-5xl py-12 mx-auto px-4">
      <div className="mb-10">
        <h1 className="text-3xl font-display font-bold text-foreground">Central de Suporte</h1>
        <p className="text-muted-foreground mt-1">Como podemos te ajudar hoje?</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <Card className="shadow-sm border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Ticket className="w-5 h-5 text-primary" /> Abrir Novo Chamado</CardTitle>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="subject"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Assunto</FormLabel>
                      <FormControl><Input placeholder="Dúvida sobre candidatura..." {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="message"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Mensagem</FormLabel>
                      <FormControl><Textarea className="h-32 resize-none" placeholder="Descreva seu problema com detalhes..." {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button type="submit" className="w-full font-bold" disabled={createTicket.isPending}>
                  {createTicket.isPending ? "Enviando..." : "Enviar Chamado"}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>

        <div>
          <h3 className="font-bold text-lg mb-4 text-foreground">Meus Chamados Recentes</h3>
          {tickets && tickets.length > 0 ? (
            <div className="space-y-3">
              {tickets.map((ticket) => (
                <div key={ticket.id} className="bg-card border border-border rounded-xl p-4 shadow-sm flex items-start justify-between gap-4">
                  <div>
                    <h4 className="font-bold text-sm text-foreground">{ticket.subject}</h4>
                    <p className="text-xs text-muted-foreground mt-1">{format(new Date(ticket.created_at), "dd/MM/yyyy HH:mm", { locale: ptBR })}</p>
                  </div>
                  <div className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 ${
                    ticket.status === 'open' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
                  }`}>
                    {ticket.status === 'open' ? <Clock className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                    {ticket.status === 'open' ? 'Aberto' : 'Resolvido'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 border-dashed border-2 border-border rounded-xl bg-muted/20">
              <p className="text-muted-foreground text-sm">Você ainda não tem nenhum chamado aberto.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

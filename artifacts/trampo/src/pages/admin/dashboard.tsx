import { useGetAdminStats } from "@workspace/api-client-react";
import { Card, CardContent } from "@/components/ui/card";
import { Users, Briefcase, FileText, Zap, Loader2, Activity } from "lucide-react";

export default function AdminDashboard() {
  const { data: stats, isLoading } = useGetAdminStats();

  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;

  const cards = [
    { title: "Total de Usuários", value: stats?.total_users || 0, icon: <Users className="w-6 h-6 text-blue-500" />, bg: "bg-blue-50" },
    { title: "Candidatos", value: stats?.total_candidates || 0, icon: <Users className="w-6 h-6 text-indigo-500" />, bg: "bg-indigo-50" },
    { title: "Empresas", value: stats?.total_recruiters || 0, icon: <Briefcase className="w-6 h-6 text-amber-500" />, bg: "bg-amber-50" },
    { title: "Vagas Criadas", value: stats?.total_jobs || 0, icon: <TargetIcon className="w-6 h-6 text-emerald-500" />, bg: "bg-emerald-50" },
    { title: "Candidaturas Totais", value: stats?.total_applications || 0, icon: <FileText className="w-6 h-6 text-purple-500" />, bg: "bg-purple-50" },
    { title: "Assinantes Premium", value: stats?.premium_users || 0, icon: <Zap className="w-6 h-6 text-orange-500" />, bg: "bg-orange-50" },
  ];

  return (
    <div className="container max-w-7xl py-12 mx-auto px-4 bg-muted/20 min-h-[80vh]">
      <div className="mb-10 flex items-center gap-3">
        <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center text-white">
          <Activity className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-3xl font-display font-bold text-foreground">Admin Dashboard</h1>
          <p className="text-muted-foreground text-sm">Visão geral do sistema TRAMPO</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card, i) => (
          <Card key={i} className="border-none shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-muted-foreground mb-2">{card.title}</p>
                <h3 className="text-4xl font-display font-bold text-foreground">{card.value.toLocaleString('pt-BR')}</h3>
              </div>
              <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${card.bg}`}>
                {card.icon}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// Inline TargetIcon to avoid extra imports
function TargetIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
  );
}

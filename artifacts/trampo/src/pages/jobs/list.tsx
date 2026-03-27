import { useState } from "react";
import { useListJobs, ListJobsWorkMode, ListJobsContractType } from "@workspace/api-client-react";
import { JobCard } from "@/components/JobCard";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, MapPin, Loader2 } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export default function JobsList() {
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");
  const [workMode, setWorkMode] = useState<ListJobsWorkMode | "">("");
  const [contractType, setContractType] = useState<ListJobsContractType | "">("");

  // Debounce search state could be added here, but for simplicity we rely on manual triggering or rapid updates
  const [appliedFilters, setAppliedFilters] = useState({ search: "", location: "", workMode: "" as any, contractType: "" as any });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setAppliedFilters({ search, location, workMode, contractType });
  };

  const { data, isLoading, isError } = useListJobs({
    search: appliedFilters.search || undefined,
    location: appliedFilters.location || undefined,
    work_mode: appliedFilters.workMode || undefined,
    contract_type: appliedFilters.contractType || undefined,
    page: 1,
    limit: 50,
  });

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-foreground mb-2">Vagas Disponíveis</h1>
        <p className="text-muted-foreground text-lg">Encontre a oportunidade ideal para sua carreira com o TRAMPO.</p>
      </div>

      {/* Filters */}
      <form onSubmit={handleSearch} className="bg-card p-4 rounded-2xl border border-border shadow-sm mb-10 flex flex-col md:flex-row gap-4 items-end">
        <div className="flex-1 w-full space-y-1">
          <label className="text-xs font-semibold text-muted-foreground uppercase">Cargo ou Palavra-chave</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              value={search} 
              onChange={(e) => setSearch(e.target.value)} 
              placeholder="Ex: Desenvolvedor React..." 
              className="pl-9 bg-background"
            />
          </div>
        </div>

        <div className="flex-1 w-full space-y-1">
          <label className="text-xs font-semibold text-muted-foreground uppercase">Localização</label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              value={location} 
              onChange={(e) => setLocation(e.target.value)} 
              placeholder="Ex: São Paulo, SP" 
              className="pl-9 bg-background"
            />
          </div>
        </div>

        <div className="w-full md:w-48 space-y-1">
          <label className="text-xs font-semibold text-muted-foreground uppercase">Modalidade</label>
          <Select value={workMode} onValueChange={(val) => setWorkMode(val as ListJobsWorkMode)}>
            <SelectTrigger className="bg-background">
              <SelectValue placeholder="Todas" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="any">Todas</SelectItem>
              <SelectItem value="remote">Remoto</SelectItem>
              <SelectItem value="hybrid">Híbrido</SelectItem>
              <SelectItem value="onsite">Presencial</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="w-full md:w-48 space-y-1">
          <label className="text-xs font-semibold text-muted-foreground uppercase">Contrato</label>
          <Select value={contractType} onValueChange={(val) => setContractType(val as ListJobsContractType)}>
            <SelectTrigger className="bg-background">
              <SelectValue placeholder="Todos" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="any">Todos</SelectItem>
              <SelectItem value="clt">CLT</SelectItem>
              <SelectItem value="pj">PJ</SelectItem>
              <SelectItem value="freelancer">Freelancer</SelectItem>
              <SelectItem value="internship">Estágio</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Button type="submit" className="w-full md:w-auto px-8 h-10 bg-primary text-primary-foreground hover-elevate">
          Buscar
        </Button>
      </form>

      {/* Results */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="border border-border rounded-xl p-6 space-y-4">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-20 w-full" />
            </div>
          ))}
        </div>
      ) : isError ? (
        <div className="text-center py-12 bg-destructive/10 text-destructive rounded-xl border border-destructive/20">
          <p className="font-bold">Erro ao carregar vagas. Tente novamente mais tarde.</p>
        </div>
      ) : data?.jobs.length === 0 ? (
        <div className="text-center py-20 bg-muted/30 rounded-2xl border border-dashed border-border">
          <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-bold mb-2">Nenhuma vaga encontrada</h3>
          <p className="text-muted-foreground">Tente ajustar seus filtros para ver mais resultados.</p>
          <Button variant="outline" className="mt-6" onClick={() => {
            setSearch(""); setLocation(""); setWorkMode(""); setContractType("");
            setAppliedFilters({ search: "", location: "", workMode: "" as any, contractType: "" as any });
          }}>
            Limpar Filtros
          </Button>
        </div>
      ) : (
        <>
          <div className="mb-4 text-sm font-medium text-muted-foreground">
            Encontramos <span className="text-primary font-bold">{data?.total || 0}</span> vagas
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data?.jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

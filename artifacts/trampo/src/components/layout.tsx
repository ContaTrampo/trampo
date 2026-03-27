import { ReactNode } from "react";
import { Link, useLocation } from "wouter";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Briefcase, User, LogOut, Menu, Zap, Target, LayoutDashboard, Ticket } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

export function Navbar() {
  const { user, logout } = useAuth();
  const [location] = useLocation();

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/">
            <div className="flex items-center gap-2 cursor-pointer">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground">
                <Target className="w-5 h-5" />
              </div>
              <span className="font-display font-bold text-xl tracking-tight text-primary">TRAMPO</span>
            </div>
          </Link>

          <div className="hidden md:flex items-center gap-6 text-sm font-medium">
            <Link href="/vagas" className={`hover:text-primary transition-colors ${location === '/vagas' ? 'text-primary' : 'text-muted-foreground'}`}>
              Explorar Vagas
            </Link>
            
            {user?.role === 'candidate' && (
              <>
                <Link href="/minhas-candidaturas" className={`hover:text-primary transition-colors ${location === '/minhas-candidaturas' ? 'text-primary' : 'text-muted-foreground'}`}>
                  Candidaturas
                </Link>
                <Link href="/suporte" className={`hover:text-primary transition-colors ${location === '/suporte' ? 'text-primary' : 'text-muted-foreground'}`}>
                  Suporte
                </Link>
              </>
            )}

            {user?.role === 'recruiter' && (
              <>
                <Link href="/recrutador" className={`hover:text-primary transition-colors ${location === '/recrutador' ? 'text-primary' : 'text-muted-foreground'}`}>
                  Meu Painel
                </Link>
              </>
            )}

            {user?.role === 'admin' && (
              <Link href="/admin" className={`hover:text-primary transition-colors ${location === '/admin' ? 'text-primary' : 'text-muted-foreground'}`}>
                Admin Dashboard
              </Link>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4">
          {!user ? (
            <div className="hidden md:flex items-center gap-4">
              <Button variant="ghost" asChild>
                <Link href="/login">Entrar</Link>
              </Button>
              <Button className="bg-accent text-accent-foreground hover:bg-accent/90" asChild>
                <Link href="/cadastro">Cadastre-se</Link>
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-4">
              {!user.is_premium && user.role !== 'admin' && (
                <Button variant="outline" size="sm" className="hidden sm:flex border-accent text-accent-foreground bg-accent/10 hover:bg-accent/20" asChild>
                  <Link href="/premium"><Zap className="w-4 h-4 mr-2" /> Seja Premium</Link>
                </Button>
              )}
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="rounded-full bg-primary/10 text-primary hover:bg-primary/20">
                    <User className="w-5 h-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="flex items-center justify-start gap-2 p-2">
                    <div className="flex flex-col space-y-1 leading-none">
                      <p className="font-medium">{user.name}</p>
                      <p className="w-[200px] truncate text-sm text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                  {user.role === 'candidate' && (
                    <DropdownMenuItem asChild>
                      <Link href="/perfil" className="w-full cursor-pointer"><User className="mr-2 w-4 h-4" /> Meu Perfil</Link>
                    </DropdownMenuItem>
                  )}
                  {user.role === 'recruiter' && (
                    <DropdownMenuItem asChild>
                      <Link href="/recrutador" className="w-full cursor-pointer"><LayoutDashboard className="mr-2 w-4 h-4" /> Painel</Link>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem asChild>
                    <Link href="/premium" className="w-full cursor-pointer"><Zap className="mr-2 w-4 h-4" /> Premium</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/suporte" className="w-full cursor-pointer"><Ticket className="mr-2 w-4 h-4" /> Suporte</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={logout} className="text-destructive focus:text-destructive cursor-pointer">
                    <LogOut className="mr-2 w-4 h-4" /> Sair
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          )}

          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="w-6 h-6" />
          </Button>
        </div>
      </div>
    </nav>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-border/50 bg-background py-12 mt-auto">
      <div className="container mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Target className="w-6 h-6 text-primary" />
            <span className="font-display font-bold text-xl text-primary">TRAMPO</span>
          </div>
          <p className="text-sm text-muted-foreground">
            A plataforma definitiva de carreiras no Brasil. Conectando talentos às melhores empresas com o poder da Inteligência Artificial.
          </p>
        </div>
        <div>
          <h4 className="font-semibold mb-4 text-foreground">Candidatos</h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li><Link href="/vagas" className="hover:text-primary">Buscar Vagas</Link></li>
            <li><Link href="/cadastro" className="hover:text-primary">Criar Perfil</Link></li>
            <li><Link href="/premium" className="hover:text-primary">Trampo Premium</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-4 text-foreground">Empresas</h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li><Link href="/cadastro" className="hover:text-primary">Publicar Vaga</Link></li>
            <li><Link href="/cadastro" className="hover:text-primary">Buscar Talentos</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-4 text-foreground">Suporte</h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li><Link href="/suporte" className="hover:text-primary">Central de Ajuda</Link></li>
            <li>Termos de Uso</li>
            <li>Privacidade</li>
          </ul>
        </div>
      </div>
      <div className="container mx-auto px-4 mt-12 pt-8 border-t border-border text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} TRAMPO Tech. Todos os direitos reservados.
      </div>
    </footer>
  );
}

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col font-sans text-foreground bg-background selection:bg-primary/20 selection:text-primary">
      <Navbar />
      <main className="flex-1 flex flex-col">{children}</main>
      <Footer />
    </div>
  );
}

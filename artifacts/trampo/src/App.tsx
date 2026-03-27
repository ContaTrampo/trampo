import "./lib/fetch-override"; // MUST BE FIRST
import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/lib/auth";
import Layout from "@/components/layout";
import Home from "@/pages/home";
import Login from "@/pages/login";
import Register from "@/pages/register";
import ForgotPassword from "@/pages/forgot-password";
import JobsList from "@/pages/jobs/list";
import JobDetail from "@/pages/jobs/detail";
import Profile from "@/pages/candidate/profile";
import Applications from "@/pages/candidate/applications";
import RecruiterDashboard from "@/pages/recruiter/dashboard";
import Premium from "@/pages/premium";
import Support from "@/pages/support";
import AdminDashboard from "@/pages/admin/dashboard";
import NotFound from "@/pages/not-found";

// Override fetch dynamically so it automatically adds Auth headers on every /api/ request
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  let [resource, config] = args;
  let url = typeof resource === 'string' ? resource : resource instanceof Request ? resource.url : '';
  
  if (url.includes('/api/')) {
    const token = localStorage.getItem('trampo_token');
    if (token) {
      config = config || {};
      const headers = new Headers(config.headers || {});
      headers.set('Authorization', `Bearer ${token}`);
      config.headers = headers;
    }
  }
  return originalFetch(resource, config);
};

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
            <Layout>
              <Switch>
                <Route path="/" component={Home} />
                <Route path="/login" component={Login} />
                <Route path="/cadastro" component={Register} />
                <Route path="/esqueci-senha" component={ForgotPassword} />
                <Route path="/vagas" component={JobsList} />
                <Route path="/vaga/:id" component={JobDetail} />
                <Route path="/perfil" component={Profile} />
                <Route path="/minhas-candidaturas" component={Applications} />
                <Route path="/recrutador" component={RecruiterDashboard} />
                <Route path="/premium" component={Premium} />
                <Route path="/suporte" component={Support} />
                <Route path="/admin" component={AdminDashboard} />
                <Route component={NotFound} />
              </Switch>
            </Layout>
          </WouterRouter>
          <Toaster />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;

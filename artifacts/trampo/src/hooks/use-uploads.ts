import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";

export function useUploadResume() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("resume", file);
      const token = localStorage.getItem("trampo_token");
      const res = await fetch("/api/candidates/resume/upload", {
        method: "POST",
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: formData,
      });
      if (!res.ok) throw new Error("Falha no upload");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/candidates/profile"] });
      toast({ title: "Sucesso", description: "Currículo enviado com sucesso!" });
    },
    onError: () => toast({ title: "Erro", description: "Falha ao enviar currículo", variant: "destructive" })
  });
}

export function useUploadPhoto() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("photo", file);
      const token = localStorage.getItem("trampo_token");
      const res = await fetch("/api/candidates/photo", {
        method: "POST",
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: formData,
      });
      if (!res.ok) throw new Error("Falha no upload");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/candidates/profile"] });
      toast({ title: "Sucesso", description: "Foto atualizada com sucesso!" });
    },
    onError: () => toast({ title: "Erro", description: "Falha ao atualizar foto", variant: "destructive" })
  });
}

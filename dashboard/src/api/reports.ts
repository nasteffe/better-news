import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost } from "./client";
import type { ReportEntry } from "../types/smae";

export function useReports() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: () => apiFetch<ReportEntry[]>("/reports"),
  });
}

export function useGenerateBriefing() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { since?: string; until?: string }) =>
      apiPost<{ report_id: string; filename: string }>("/reports/briefing", body),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["reports"] }),
  });
}

export function useGenerateFlashAlert() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (eventId: string) =>
      apiPost<{ report_id: string; filename: string }>("/reports/flash-alert", { event_id: eventId }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["reports"] }),
  });
}

export function useGenerateConvergence() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { since?: string; until?: string }) =>
      apiPost<{ report_id: string; filename: string }>("/reports/convergence", body),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["reports"] }),
  });
}

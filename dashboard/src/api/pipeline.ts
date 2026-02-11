import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiPost } from "./client";
import type { PipelineRun } from "../types/smae";

export function usePipelineStatus() {
  return useQuery({
    queryKey: ["pipeline-status"],
    queryFn: () => apiFetch<Record<string, unknown>>("/pipeline/status"),
    refetchInterval: 5000,
  });
}

export function usePipelineHistory() {
  return useQuery({
    queryKey: ["pipeline-history"],
    queryFn: () => apiFetch<PipelineRun[]>("/pipeline/history"),
  });
}

export function useTriggerPipeline() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (lookbackDays: number = 2) =>
      apiPost<{ run_id: string }>(`/pipeline/run?lookback_days=${lookbackDays}`, {}),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["pipeline-status"] });
      void qc.invalidateQueries({ queryKey: ["pipeline-history"] });
    },
  });
}

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { ThresholdDefinition, ThresholdStatusEntry } from "../types/smae";

export function useThresholdDefinitions() {
  return useQuery({
    queryKey: ["thresholds"],
    queryFn: () => apiFetch<ThresholdDefinition[]>("/thresholds"),
  });
}

export function useThresholdStatus() {
  return useQuery({
    queryKey: ["thresholds-status"],
    queryFn: () => apiFetch<ThresholdStatusEntry[]>("/thresholds/status"),
  });
}

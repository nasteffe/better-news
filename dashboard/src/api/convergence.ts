import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { ConvergenceMatrix, ConvergenceScore } from "../types/smae";

export function useConvergenceScores() {
  return useQuery({
    queryKey: ["convergence"],
    queryFn: () => apiFetch<ConvergenceScore[]>("/convergence"),
  });
}

export function useConvergenceMatrix() {
  return useQuery({
    queryKey: ["convergence-matrix"],
    queryFn: () => apiFetch<ConvergenceMatrix>("/convergence/matrix"),
  });
}

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { NetworkSummary } from "../types/smae";

export function useNetworks() {
  return useQuery({
    queryKey: ["networks"],
    queryFn: () => apiFetch<NetworkSummary[]>("/networks"),
  });
}

export function useNetwork(networkId: number) {
  return useQuery({
    queryKey: ["network", networkId],
    queryFn: () => apiFetch<Record<string, unknown>>(`/networks/${networkId}`),
    enabled: networkId > 0,
  });
}

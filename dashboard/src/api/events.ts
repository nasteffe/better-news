import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "./client";
import type { Event, PaginatedResponse } from "../types/smae";

interface EventFilters {
  network?: number[];
  alert_level?: string[];
  country?: string;
  since?: string;
  until?: string;
  min_ci?: number;
  limit?: number;
  offset?: number;
}

function buildParams(f: EventFilters): string {
  const p = new URLSearchParams();
  f.network?.forEach((n) => p.append("network", String(n)));
  f.alert_level?.forEach((a) => p.append("alert_level", a));
  if (f.country) p.set("country", f.country);
  if (f.since) p.set("since", f.since);
  if (f.until) p.set("until", f.until);
  if (f.min_ci) p.set("min_ci", String(f.min_ci));
  if (f.limit) p.set("limit", String(f.limit));
  if (f.offset) p.set("offset", String(f.offset));
  return p.toString();
}

export function useEvents(filters: EventFilters = {}) {
  const qs = buildParams(filters);
  return useQuery({
    queryKey: ["events", qs],
    queryFn: () => apiFetch<PaginatedResponse<Event>>(`/events?${qs}`),
  });
}

export function useEvent(eventId: string) {
  return useQuery({
    queryKey: ["event", eventId],
    queryFn: () => apiFetch<Event>(`/events/${eventId}`),
    enabled: !!eventId,
  });
}

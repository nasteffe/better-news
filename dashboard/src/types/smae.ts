/** TypeScript types mirroring the SMAE Pydantic models. */

export type AlertLevel = "WATCH" | "MONITOR" | "ALERT" | "CRITICAL" | "SYSTEMIC";
export type ThresholdStatus = "BELOW" | "APPROACHING" | "EXCEEDED";
export type ThresholdCategory = "absolute" | "rate_of_change" | "relational" | "governance_decay";
export type OntologyNode = "appropriation" | "displacement" | "governance" | "resistance";
export type AnalyticalLayer = "stock" | "flow" | "accumulation" | "externality" | "governance" | "contestation";

export interface Source {
  organization: string;
  report_name: string;
  doi: string | null;
  report_id: string | null;
  tier: number;
  access_date: string;
  provisional: boolean;
}

export interface Actor {
  name: string;
  actor_type: string;
  jurisdiction: string | null;
  role: string;
}

export interface ThresholdMetric {
  name: string;
  category: ThresholdCategory;
  networks: number[];
  baseline_value: number;
  baseline_date: string;
  delta: number;
  current_value: number;
  threshold_value: number;
  unit: string;
  status: ThresholdStatus;
}

export interface ThresholdCrossing {
  metric: ThresholdMetric;
  detected_at: string;
  alert_level: AlertLevel;
  notes: string;
}

export interface Event {
  id: string;
  title: string;
  summary: string;
  event_date: string;
  detected_at: string;
  country: string;
  region: string | null;
  coordinates: [number, number] | null;
  networks: number[];
  layers: AnalyticalLayer[];
  nodes: OntologyNode[];
  coupling_patterns: number[];
  actors: Actor[];
  threshold_crossings: ThresholdCrossing[];
  sources: Source[];
  alert_level: AlertLevel;
  resistance_summary: string | null;
  governance_context: string | null;
  outlook_30d: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface NetworkSummary {
  network_id: number;
  roman: string;
  label: string;
  event_count: number;
  convergent_count: number;
  threshold_crossings: number;
  max_alert: AlertLevel;
}

export interface ConvergenceScore {
  event_id: string;
  networks: number[];
  severity_weights: Record<number, number>;
}

export interface ConvergenceMatrix {
  labels: string[];
  matrix: number[][];
}

export interface ThresholdDefinition {
  name: string;
  category: ThresholdCategory;
  description: string;
  networks: number[];
  threshold_value: number;
  unit: string;
}

export interface ThresholdStatusEntry {
  event_id: string;
  event_title: string;
  metric_name: string;
  category: string;
  baseline_value: number;
  baseline_date: string;
  delta: number;
  current_value: number;
  threshold_value: number;
  unit: string;
  status: ThresholdStatus;
  alert_level: AlertLevel;
  comparison: string;
}

export interface PipelineRun {
  id: string;
  run_date: string;
  started_at: string;
  finished_at: string | null;
  status: string;
  events_ingested: number;
  threshold_crossings: number;
  convergence_nodes: number;
  source_errors: string[];
}

export interface ReportEntry {
  id: string;
  created_at: string;
  report_type: string;
  filename: string;
}

export const NETWORK_LABELS: Record<number, string> = {
  1: "Carbon Accumulation",
  2: "Water Appropriation",
  3: "Soil Fertility Transfer",
  4: "Mineral Extraction",
  5: "Atmospheric Commons",
  6: "Biodiversity & Genetic",
  7: "Ocean & Marine",
  8: "Labor & Health",
};

export const NETWORK_ROMAN: Record<number, string> = {
  1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII",
};

export const COUPLING_PATTERN_LABELS: Record<number, string> = {
  1: "Extractive Cascade",
  2: "Regulatory Arbitrage Loop",
  3: "Green Transition Paradox",
  4: "Atmospheric Enclosure",
  5: "Debt-Nature Trap",
  6: "Sacrifice Zone Spiral",
  7: "Militarized Conservation",
  8: "Food Sovereignty Erosion",
  9: "Humanitarian-Security Feedback",
  10: "Knowledge Enclosure Circuit",
  11: "Infrastructure Lock-in Ratchet",
};

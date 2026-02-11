import type { AlertLevel } from "../../types/smae";

const COLORS: Record<AlertLevel, string> = {
  WATCH: "bg-gray-500",
  MONITOR: "bg-blue-600",
  ALERT: "bg-amber-600",
  CRITICAL: "bg-red-600",
  SYSTEMIC: "bg-smae-dark-red",
};

export default function AlertBadge({ level }: { level: AlertLevel }) {
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-xs font-bold text-white ${COLORS[level]}`}
    >
      {level}
    </span>
  );
}

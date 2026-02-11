import type { ThresholdStatusEntry } from "../../types/smae";

const STATUS_COLORS = {
  BELOW: "bg-threshold-below",
  APPROACHING: "bg-threshold-approaching",
  EXCEEDED: "bg-threshold-exceeded",
};

export default function ThresholdGauge({ entry }: { entry: ThresholdStatusEntry }) {
  const pct = Math.min(
    (entry.current_value / entry.threshold_value) * 100,
    120
  );

  return (
    <div className="rounded border border-gray-200 bg-white p-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-smae-body">{entry.metric_name}</span>
        <span
          className={`rounded px-1.5 py-0.5 text-xs font-bold text-white ${STATUS_COLORS[entry.status]}`}
        >
          {entry.status}
        </span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-gray-200">
        <div
          className={`h-2 rounded-full transition-all ${STATUS_COLORS[entry.status]}`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
      <div className="mt-1 flex justify-between text-xs text-smae-source">
        <span>
          {entry.current_value.toLocaleString()} {entry.unit}
        </span>
        <span>Threshold: {entry.threshold_value.toLocaleString()}</span>
      </div>
    </div>
  );
}

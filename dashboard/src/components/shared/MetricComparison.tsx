import type { ThresholdMetric } from "../../types/smae";

const STATUS_COLORS = {
  BELOW: "text-threshold-below",
  APPROACHING: "text-threshold-approaching",
  EXCEEDED: "text-threshold-exceeded",
};

export default function MetricComparison({ metric }: { metric: ThresholdMetric }) {
  return (
    <div className="font-mono text-xs leading-snug">
      <span className="text-smae-metric">
        {metric.baseline_value.toLocaleString()} {metric.unit} ({metric.baseline_date})
        {" + "}
        {metric.delta >= 0 ? "+" : ""}
        {metric.delta.toLocaleString()}
        {" = "}
        {metric.current_value.toLocaleString()}
        {" \u2264 "}
        {metric.threshold_value.toLocaleString()}
      </span>
      <span className={`ml-2 font-bold ${STATUS_COLORS[metric.status]}`}>
        [{metric.status}]
      </span>
    </div>
  );
}

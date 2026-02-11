import type { ThresholdDefinition } from "../../types/smae";
import { NETWORK_ROMAN } from "../../types/smae";

const CATEGORY_LABELS: Record<string, string> = {
  absolute: "Absolute (Bright Lines)",
  rate_of_change: "Rate-of-Change (Velocity)",
  relational: "Relational (Equity)",
  governance_decay: "Governance Decay",
};

export default function ThresholdGrid({
  definitions,
}: {
  definitions: ThresholdDefinition[];
}) {
  const grouped = definitions.reduce<Record<string, ThresholdDefinition[]>>(
    (acc, t) => {
      const cat = t.category;
      if (!acc[cat]) acc[cat] = [];
      acc[cat]!.push(t);
      return acc;
    },
    {}
  );

  return (
    <div className="space-y-6">
      {Object.entries(grouped).map(([category, defs]) => (
        <div key={category}>
          <h3 className="mb-2 text-sm font-bold text-smae-dark-blue">
            {CATEGORY_LABELS[category] ?? category}
          </h3>
          <div className="grid gap-2 md:grid-cols-2">
            {defs.map((d) => (
              <div
                key={d.name}
                className="rounded border border-gray-200 bg-white p-3"
              >
                <div className="text-xs font-medium text-smae-body">{d.name}</div>
                <p className="mt-1 text-xs text-smae-source">{d.description}</p>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="font-mono text-smae-metric">
                    {d.threshold_value.toLocaleString()} {d.unit}
                  </span>
                  <span className="text-smae-source">
                    {d.networks.map((n) => NETWORK_ROMAN[n]).join(", ")}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

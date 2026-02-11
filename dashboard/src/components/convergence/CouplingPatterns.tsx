import type { Event } from "../../types/smae";
import { COUPLING_PATTERN_LABELS } from "../../types/smae";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function CouplingPatterns({ events }: { events: Event[] }) {
  const counts: Record<number, number> = {};
  for (const e of events) {
    for (const p of e.coupling_patterns) {
      counts[p] = (counts[p] ?? 0) + 1;
    }
  }

  const data = Object.entries(counts)
    .map(([id, count]) => ({
      name: COUPLING_PATTERN_LABELS[Number(id)] ?? `Pattern ${id}`,
      count,
    }))
    .sort((a, b) => b.count - a.count);

  if (data.length === 0) {
    return (
      <p className="text-xs text-smae-source">No coupling patterns identified.</p>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-bold text-smae-dark-blue">
        Structural Coupling Patterns
      </h3>
      <ResponsiveContainer width="100%" height={data.length * 32 + 20}>
        <BarChart data={data} layout="vertical" margin={{ left: 150 }}>
          <XAxis type="number" allowDecimals={false} tick={{ fontSize: 10 }} />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 10 }}
            width={140}
          />
          <Tooltip />
          <Bar dataKey="count" fill="#b8860b" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

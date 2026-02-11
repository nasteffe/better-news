import type { Event, AlertLevel } from "../../types/smae";

const DOT_COLORS: Record<AlertLevel, string> = {
  WATCH: "#6b7280",
  MONITOR: "#2563eb",
  ALERT: "#b8860b",
  CRITICAL: "#dc2626",
  SYSTEMIC: "#8b0000",
};

/**
 * Simple SVG world map with event markers.
 * Uses a basic Mercator-like projection on an SVG canvas.
 * A full Leaflet/MapLibre integration can replace this later.
 */
export default function EventMap({ events }: { events: Event[] }) {
  const geoEvents = events.filter((e) => e.coordinates !== null);

  // Simple equirectangular projection to SVG coordinates
  const toSvg = (lat: number, lon: number): [number, number] => {
    const x = ((lon + 180) / 360) * 800;
    const y = ((90 - lat) / 180) * 400;
    return [x, y];
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-bold text-smae-dark-blue">
        Event Geographic Distribution
      </h3>
      {geoEvents.length === 0 ? (
        <p className="text-xs text-smae-source">
          No events with coordinate data. Events with coordinates will appear as markers.
        </p>
      ) : null}
      <svg
        viewBox="0 0 800 400"
        className="w-full rounded border border-gray-100 bg-blue-50/30"
      >
        {/* Simple continent outlines (rough) */}
        <rect x="0" y="0" width="800" height="400" fill="#f0f7ff" />
        <text x="400" y="200" textAnchor="middle" className="text-xs" fill="#cbd5e1">
          World Map
        </text>

        {/* Event markers */}
        {geoEvents.map((e) => {
          const [lat, lon] = e.coordinates!;
          const [x, y] = toSvg(lat, lon);
          const r = Math.max(3, Math.min(e.networks.length * 2, 10));
          return (
            <g key={e.id}>
              <circle
                cx={x}
                cy={y}
                r={r}
                fill={DOT_COLORS[e.alert_level]}
                opacity={0.8}
                stroke="white"
                strokeWidth={1}
              />
              <title>
                {e.country}: {e.title} (CI {e.networks.length}, {e.alert_level})
              </title>
            </g>
          );
        })}
      </svg>
      <div className="mt-2 flex gap-3 text-xs text-smae-source">
        {Object.entries(DOT_COLORS).map(([level, color]) => (
          <div key={level} className="flex items-center gap-1">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: color }}
            />
            {level}
          </div>
        ))}
      </div>
    </div>
  );
}

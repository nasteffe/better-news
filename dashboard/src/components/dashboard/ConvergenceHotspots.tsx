import { Link } from "react-router-dom";
import type { Event } from "../../types/smae";
import AlertBadge from "../shared/AlertBadge";
import NetworkBadge from "../shared/NetworkBadge";

export default function ConvergenceHotspots({ events }: { events: Event[] }) {
  const sorted = [...events]
    .filter((e) => e.networks.length >= 2)
    .sort((a, b) => b.networks.length - a.networks.length)
    .slice(0, 5);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-bold text-smae-dark-amber">
        Convergence Hotspots
      </h3>
      {sorted.length === 0 ? (
        <p className="text-xs text-smae-source">No convergence nodes detected.</p>
      ) : (
        <div className="space-y-3">
          {sorted.map((e) => (
            <Link
              key={e.id}
              to={`/events/${e.id}`}
              className="block rounded border border-gray-100 p-2 hover:bg-stone-50"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-smae-body">
                  {e.country}: {e.title.slice(0, 50)}
                </span>
                <AlertBadge level={e.alert_level} />
              </div>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-xs font-bold text-smae-dark-amber">
                  CI {e.networks.length}
                </span>
                <div className="flex flex-wrap">
                  {e.networks.map((n) => (
                    <NetworkBadge key={n} id={n} />
                  ))}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

import { Link } from "react-router-dom";
import type { Event } from "../../types/smae";
import AlertBadge from "../shared/AlertBadge";

export default function AlertTicker({ events }: { events: Event[] }) {
  const critical = events.filter(
    (e) => e.alert_level === "CRITICAL" || e.alert_level === "SYSTEMIC"
  );

  if (critical.length === 0) return null;

  return (
    <div className="overflow-hidden rounded border border-red-200 bg-red-50 px-4 py-2">
      <div className="flex items-center gap-4 overflow-x-auto whitespace-nowrap">
        <span className="shrink-0 text-xs font-bold uppercase text-smae-dark-red">
          Active Alerts
        </span>
        {critical.map((e) => (
          <Link
            key={e.id}
            to={`/events/${e.id}`}
            className="flex shrink-0 items-center gap-2 text-sm hover:underline"
          >
            <AlertBadge level={e.alert_level} />
            <span className="text-smae-body">
              {e.country}: {e.title.length > 60 ? e.title.slice(0, 60) + "..." : e.title}
            </span>
            <span className="text-xs text-smae-source">CI {e.networks.length}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}

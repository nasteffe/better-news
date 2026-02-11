import { Link } from "react-router-dom";
import type { Event } from "../../types/smae";
import AlertBadge from "../shared/AlertBadge";
import NetworkBadge from "../shared/NetworkBadge";

export default function EventCard({ event }: { event: Event }) {
  const hasResistance =
    event.resistance_summary &&
    !event.resistance_summary.includes("[PENDING]");

  return (
    <Link
      to={`/events/${event.id}`}
      className="block rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <AlertBadge level={event.alert_level} />
            <span className="text-xs text-smae-source">{event.event_date}</span>
            <span className="text-xs font-medium text-smae-dark-amber">
              CI {event.networks.length}
            </span>
            {hasResistance && (
              <span className="inline-block h-2 w-2 rounded-full bg-smae-dark-green" title="Resistance data present" />
            )}
          </div>
          <h3 className="mt-1 text-sm font-medium text-smae-body">
            {event.country}: {event.title}
          </h3>
          <p className="mt-1 text-xs text-smae-subhead line-clamp-2">
            {event.summary}
          </p>
        </div>
      </div>
      <div className="mt-2 flex flex-wrap gap-0.5">
        {event.networks.map((n) => (
          <NetworkBadge key={n} id={n} />
        ))}
      </div>
      {event.threshold_crossings.length > 0 && (
        <div className="mt-2 text-xs text-smae-dark-red font-medium">
          {event.threshold_crossings.length} threshold crossing(s)
        </div>
      )}
    </Link>
  );
}

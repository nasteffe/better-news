import { Link } from "react-router-dom";
import type { NetworkSummary, AlertLevel } from "../../types/smae";

const ALERT_BG: Record<AlertLevel, string> = {
  WATCH: "bg-gray-100 text-gray-600",
  MONITOR: "bg-blue-100 text-blue-700",
  ALERT: "bg-amber-100 text-amber-700",
  CRITICAL: "bg-red-100 text-red-700",
  SYSTEMIC: "bg-red-200 text-smae-dark-red",
};

export default function NetworkCard({ network }: { network: NetworkSummary }) {
  return (
    <Link
      to={`/networks/${network.network_id}`}
      className="block rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-bold text-smae-dark-blue">
          {network.roman}
        </span>
        <span
          className={`rounded px-2 py-0.5 text-xs font-medium ${ALERT_BG[network.max_alert]}`}
        >
          {network.max_alert}
        </span>
      </div>
      <h3 className="mt-1 text-xs font-medium text-smae-body">{network.label}</h3>
      <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
        <div>
          <div className="text-lg font-bold text-smae-body">{network.event_count}</div>
          <div className="text-smae-source">Events</div>
        </div>
        <div>
          <div className="text-lg font-bold text-smae-dark-amber">{network.convergent_count}</div>
          <div className="text-smae-source">Convergent</div>
        </div>
        <div>
          <div className="text-lg font-bold text-smae-dark-red">{network.threshold_crossings}</div>
          <div className="text-smae-source">Crossings</div>
        </div>
      </div>
    </Link>
  );
}

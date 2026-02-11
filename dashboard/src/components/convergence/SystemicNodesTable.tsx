import { Link } from "react-router-dom";
import type { Event } from "../../types/smae";
import { NETWORK_ROMAN } from "../../types/smae";
import AlertBadge from "../shared/AlertBadge";

export default function SystemicNodesTable({ events }: { events: Event[] }) {
  const systemic = [...events]
    .filter((e) => e.networks.length >= 4)
    .sort((a, b) => b.networks.length - a.networks.length);

  if (systemic.length === 0) {
    return (
      <p className="text-xs text-smae-source">No systemic nodes (CI {"\u2265"} 4) detected.</p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b bg-smae-dark-amber text-white">
            <th className="p-2 text-left">Event</th>
            <th className="p-2 text-left">Country</th>
            <th className="p-2 text-center">CI</th>
            <th className="p-2 text-left">Networks</th>
            <th className="p-2 text-center">Alert</th>
          </tr>
        </thead>
        <tbody>
          {systemic.map((e) => (
            <tr key={e.id} className="border-b hover:bg-stone-50">
              <td className="p-2">
                <Link to={`/events/${e.id}`} className="text-smae-dark-blue hover:underline">
                  {e.title.slice(0, 50)}
                </Link>
              </td>
              <td className="p-2">{e.country}</td>
              <td className="p-2 text-center font-bold text-smae-dark-amber">
                {e.networks.length}
              </td>
              <td className="p-2">
                {e.networks.map((n) => NETWORK_ROMAN[n]).join(", ")}
              </td>
              <td className="p-2 text-center">
                <AlertBadge level={e.alert_level} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

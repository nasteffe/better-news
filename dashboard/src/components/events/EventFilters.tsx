import { NETWORK_LABELS, NETWORK_ROMAN } from "../../types/smae";
import type { AlertLevel } from "../../types/smae";

const ALERT_LEVELS: AlertLevel[] = ["WATCH", "MONITOR", "ALERT", "CRITICAL", "SYSTEMIC"];

interface Props {
  selectedNetworks: number[];
  setSelectedNetworks: (n: number[]) => void;
  selectedAlerts: string[];
  setSelectedAlerts: (a: string[]) => void;
  country: string;
  setCountry: (c: string) => void;
  minCi: number;
  setMinCi: (n: number) => void;
}

export default function EventFilters({
  selectedNetworks,
  setSelectedNetworks,
  selectedAlerts,
  setSelectedAlerts,
  country,
  setCountry,
  minCi,
  setMinCi,
}: Props) {
  const toggleNetwork = (id: number) => {
    setSelectedNetworks(
      selectedNetworks.includes(id)
        ? selectedNetworks.filter((n) => n !== id)
        : [...selectedNetworks, id]
    );
  };

  const toggleAlert = (level: string) => {
    setSelectedAlerts(
      selectedAlerts.includes(level)
        ? selectedAlerts.filter((a) => a !== level)
        : [...selectedAlerts, level]
    );
  };

  return (
    <div className="space-y-4">
      <div>
        <h4 className="mb-2 text-xs font-bold uppercase text-smae-subhead">Networks</h4>
        <div className="space-y-1">
          {Object.entries(NETWORK_LABELS).map(([id, label]) => (
            <label key={id} className="flex items-center gap-2 text-xs">
              <input
                type="checkbox"
                checked={selectedNetworks.includes(Number(id))}
                onChange={() => toggleNetwork(Number(id))}
                className="rounded border-gray-300"
              />
              <span>{NETWORK_ROMAN[Number(id)]}: {label}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h4 className="mb-2 text-xs font-bold uppercase text-smae-subhead">Alert Level</h4>
        <div className="space-y-1">
          {ALERT_LEVELS.map((level) => (
            <label key={level} className="flex items-center gap-2 text-xs">
              <input
                type="checkbox"
                checked={selectedAlerts.includes(level)}
                onChange={() => toggleAlert(level)}
                className="rounded border-gray-300"
              />
              <span>{level}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h4 className="mb-2 text-xs font-bold uppercase text-smae-subhead">Country</h4>
        <input
          type="text"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          placeholder="Filter by country..."
          className="w-full rounded border border-gray-300 px-2 py-1 text-xs"
        />
      </div>

      <div>
        <h4 className="mb-2 text-xs font-bold uppercase text-smae-subhead">Min CI</h4>
        <input
          type="range"
          min={1}
          max={8}
          value={minCi}
          onChange={(e) => setMinCi(Number(e.target.value))}
          className="w-full"
        />
        <span className="text-xs text-smae-source">CI {"\u2265"} {minCi}</span>
      </div>
    </div>
  );
}

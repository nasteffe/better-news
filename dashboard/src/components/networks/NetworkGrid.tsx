import type { NetworkSummary } from "../../types/smae";
import NetworkCard from "./NetworkCard";

export default function NetworkGrid({ networks }: { networks: NetworkSummary[] }) {
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {networks.map((n) => (
        <NetworkCard key={n.network_id} network={n} />
      ))}
    </div>
  );
}

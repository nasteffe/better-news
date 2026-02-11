import { useNetworks } from "../api/networks";
import NetworkGrid from "../components/networks/NetworkGrid";
import Spinner from "../components/shared/Spinner";

export default function NetworksPage() {
  const { data: networks, isLoading } = useNetworks();

  if (isLoading) return <Spinner />;

  return (
    <div>
      <h1 className="mb-4 text-lg font-bold text-smae-title">
        Metabolic Networks
      </h1>
      <p className="mb-4 text-xs text-smae-source">
        Eight metabolic networks through which all events are analyzed.
        Click a network for layer-by-layer detail.
      </p>
      {networks && <NetworkGrid networks={networks} />}
    </div>
  );
}

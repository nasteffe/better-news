import { useState } from "react";
import { useEvents } from "../api/events";
import EventFeed from "../components/events/EventFeed";
import EventFilters from "../components/events/EventFilters";
import Spinner from "../components/shared/Spinner";

export default function EventsPage() {
  const [selectedNetworks, setSelectedNetworks] = useState<number[]>([]);
  const [selectedAlerts, setSelectedAlerts] = useState<string[]>([]);
  const [country, setCountry] = useState("");
  const [minCi, setMinCi] = useState(1);

  const { data, isLoading } = useEvents({
    network: selectedNetworks.length ? selectedNetworks : undefined,
    alert_level: selectedAlerts.length ? selectedAlerts : undefined,
    country: country || undefined,
    min_ci: minCi > 1 ? minCi : undefined,
    limit: 100,
  });

  return (
    <div className="flex gap-6">
      <div className="w-56 shrink-0">
        <h2 className="mb-3 text-sm font-bold text-smae-dark-blue">Filters</h2>
        <EventFilters
          selectedNetworks={selectedNetworks}
          setSelectedNetworks={setSelectedNetworks}
          selectedAlerts={selectedAlerts}
          setSelectedAlerts={setSelectedAlerts}
          country={country}
          setCountry={setCountry}
          minCi={minCi}
          setMinCi={setMinCi}
        />
      </div>
      <div className="flex-1">
        <div className="mb-3 flex items-center justify-between">
          <h1 className="text-lg font-bold text-smae-title">Event Feed</h1>
          <span className="text-xs text-smae-source">
            {data?.total ?? 0} events
          </span>
        </div>
        {isLoading ? <Spinner /> : <EventFeed events={data?.items ?? []} />}
      </div>
    </div>
  );
}

import { useEvents } from "../api/events";
import EventMap from "../components/map/EventMap";
import Spinner from "../components/shared/Spinner";

export default function MapPage() {
  const { data, isLoading } = useEvents({ limit: 200 });

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-bold text-smae-title">Geographic View</h1>
      <p className="text-xs text-smae-source">
        Events plotted by coordinates. Marker color indicates alert level;
        marker size indicates convergence index.
      </p>
      <EventMap events={data?.items ?? []} />
    </div>
  );
}

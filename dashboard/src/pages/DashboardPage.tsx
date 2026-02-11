import { useEvents } from "../api/events";
import { useNetworks } from "../api/networks";
import { useThresholdStatus } from "../api/thresholds";
import AlertTicker from "../components/dashboard/AlertTicker";
import ConvergenceHotspots from "../components/dashboard/ConvergenceHotspots";
import EventFeed from "../components/events/EventFeed";
import NetworkGrid from "../components/networks/NetworkGrid";
import ThresholdGauge from "../components/thresholds/ThresholdGauge";
import Spinner from "../components/shared/Spinner";

export default function DashboardPage() {
  const { data: eventsData, isLoading: eventsLoading } = useEvents({ limit: 20 });
  const { data: networks, isLoading: networksLoading } = useNetworks();
  const { data: thresholdStatus } = useThresholdStatus();

  if (eventsLoading || networksLoading) return <Spinner />;

  const events = eventsData?.items ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-bold text-smae-title">Command Center</h1>

      {/* Alert ticker */}
      <AlertTicker events={events} />

      {/* Network status grid */}
      <div>
        <h2 className="mb-2 text-sm font-bold text-smae-dark-blue">
          Network Status
        </h2>
        {networks && <NetworkGrid networks={networks} />}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Threshold dashboard */}
        <div>
          <h2 className="mb-2 text-sm font-bold text-smae-dark-blue">
            Threshold Dashboard
          </h2>
          {thresholdStatus && thresholdStatus.length > 0 ? (
            <div className="space-y-2">
              {thresholdStatus.slice(0, 8).map((ts, i) => (
                <ThresholdGauge key={i} entry={ts} />
              ))}
            </div>
          ) : (
            <p className="text-xs text-smae-source">No threshold crossings detected.</p>
          )}
        </div>

        {/* Convergence hotspots */}
        <ConvergenceHotspots events={events} />
      </div>

      {/* Recent event feed */}
      <div>
        <h2 className="mb-2 text-sm font-bold text-smae-dark-blue">
          Recent Events
        </h2>
        <EventFeed events={events.slice(0, 10)} />
      </div>
    </div>
  );
}

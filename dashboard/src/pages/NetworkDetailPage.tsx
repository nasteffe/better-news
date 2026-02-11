import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useNetwork } from "../api/networks";
import Spinner from "../components/shared/Spinner";
import AlertBadge from "../components/shared/AlertBadge";
import type { AlertLevel, AnalyticalLayer } from "../types/smae";

const LAYERS: AnalyticalLayer[] = [
  "stock", "flow", "accumulation", "externality", "governance", "contestation",
];

export default function NetworkDetailPage() {
  const { id } = useParams<{ id: string }>();
  const networkId = Number(id);
  const { data, isLoading } = useNetwork(networkId);
  const [activeLayer, setActiveLayer] = useState<AnalyticalLayer>("flow");

  if (isLoading) return <Spinner />;
  if (!data) {
    return (
      <div className="p-8 text-center">
        <p className="text-sm text-smae-dark-red">Network not found.</p>
        <Link to="/networks" className="text-xs text-smae-dark-blue hover:underline">
          Back to networks
        </Link>
      </div>
    );
  }

  const layers = data.layers as Record<string, { id: string; title: string; country: string; alert_level: AlertLevel; event_date: string }[]>;
  const resistance = data.resistance_spotlight as { id: string; title: string; country: string; resistance_summary: string }[];
  const layerEvents = layers[activeLayer] ?? [];

  return (
    <div>
      <Link to="/networks" className="text-xs text-smae-dark-blue hover:underline">
        {"\u2190"} Back to networks
      </Link>
      <h1 className="mt-2 text-lg font-bold text-smae-title">
        Network {String(data.roman)}: {String(data.label)}
      </h1>
      <p className="text-xs text-smae-source">{String(data.event_count)} events</p>

      {/* Layer tabs */}
      <div className="mt-4 flex gap-1 border-b border-gray-200">
        {LAYERS.map((layer) => (
          <button
            key={layer}
            onClick={() => setActiveLayer(layer)}
            className={`px-3 py-2 text-xs font-medium transition-colors ${
              activeLayer === layer
                ? "border-b-2 border-smae-dark-blue text-smae-dark-blue"
                : "text-smae-source hover:text-smae-body"
            }`}
          >
            {layer.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Layer events */}
      <div className="mt-4 space-y-2">
        {layerEvents.length === 0 ? (
          <p className="text-xs text-smae-source">No events in this layer.</p>
        ) : (
          layerEvents.map((e) => (
            <Link
              key={e.id}
              to={`/events/${e.id}`}
              className="flex items-center justify-between rounded border border-gray-200 bg-white p-3 hover:bg-stone-50"
            >
              <div>
                <span className="text-sm font-medium text-smae-body">
                  {e.country}: {e.title}
                </span>
                <span className="ml-2 text-xs text-smae-source">{e.event_date}</span>
              </div>
              <AlertBadge level={e.alert_level} />
            </Link>
          ))
        )}
      </div>

      {/* Resistance spotlight */}
      {resistance.length > 0 && (
        <div className="mt-6">
          <h2 className="mb-2 text-sm font-bold text-smae-dark-green">
            Resistance Spotlight
          </h2>
          <div className="space-y-2">
            {resistance.map((r) => (
              <Link
                key={r.id}
                to={`/events/${r.id}`}
                className="block rounded border border-green-200 bg-green-50 p-3 hover:bg-green-100"
              >
                <div className="text-xs font-medium text-smae-body">
                  {r.country}: {r.title}
                </div>
                <p className="mt-1 text-xs italic text-smae-dark-green">
                  {r.resistance_summary}
                </p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

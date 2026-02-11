import type { Event } from "../../types/smae";
import { COUPLING_PATTERN_LABELS } from "../../types/smae";
import AlertBadge from "../shared/AlertBadge";
import MetricComparison from "../shared/MetricComparison";
import NetworkBadge from "../shared/NetworkBadge";

export default function EventDetail({ event }: { event: Event }) {
  const hasResistance =
    event.resistance_summary && !event.resistance_summary.includes("[PENDING]");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3">
          <AlertBadge level={event.alert_level} />
          <span className="text-xs text-smae-source">{event.event_date}</span>
          <span className="text-sm font-bold text-smae-dark-amber">
            CI {event.networks.length}
          </span>
        </div>
        <h1 className="mt-2 text-lg font-bold text-smae-title">
          {event.country}: {event.title}
        </h1>
        {event.region && (
          <span className="text-xs text-smae-source">Region: {event.region}</span>
        )}
      </div>

      {/* Network tags */}
      <div>
        <h2 className="mb-1 text-xs font-bold uppercase text-smae-dark-blue">Networks</h2>
        <div className="flex flex-wrap">
          {event.networks.map((n) => (
            <NetworkBadge key={n} id={n} />
          ))}
        </div>
      </div>

      {/* Ontology nodes */}
      <div className="flex gap-2">
        {event.nodes.map((node) => (
          <span
            key={node}
            className={`rounded px-2 py-0.5 text-xs font-medium ${
              node === "resistance"
                ? "bg-green-100 text-smae-dark-green"
                : node === "appropriation" || node === "displacement"
                  ? "bg-red-100 text-smae-dark-red"
                  : "bg-blue-100 text-smae-dark-blue"
            }`}
          >
            {node.toUpperCase()}
          </span>
        ))}
      </div>

      {/* Summary */}
      <div>
        <h2 className="mb-1 text-xs font-bold uppercase text-smae-dark-blue">Summary</h2>
        <p className="text-sm text-smae-body">{event.summary}</p>
      </div>

      {/* Actors */}
      {event.actors.length > 0 && (
        <div>
          <h2 className="mb-2 text-xs font-bold uppercase text-smae-dark-blue">Actors</h2>
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b bg-stone-100 text-left">
                <th className="p-2">Name</th>
                <th className="p-2">Type</th>
                <th className="p-2">Jurisdiction</th>
                <th className="p-2">Role</th>
              </tr>
            </thead>
            <tbody>
              {event.actors.map((actor, i) => (
                <tr key={i} className="border-b">
                  <td className="p-2 font-medium">{actor.name}</td>
                  <td className="p-2">{actor.actor_type}</td>
                  <td className="p-2">{actor.jurisdiction ?? "—"}</td>
                  <td
                    className={`p-2 font-medium ${
                      actor.role === "resister"
                        ? "text-smae-dark-green"
                        : actor.role === "extractor"
                          ? "text-smae-dark-red"
                          : ""
                    }`}
                  >
                    {actor.role}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Threshold crossings */}
      {event.threshold_crossings.length > 0 && (
        <div>
          <h2 className="mb-2 text-xs font-bold uppercase text-smae-dark-blue">
            Threshold Crossings
          </h2>
          <div className="space-y-2">
            {event.threshold_crossings.map((tc, i) => (
              <div key={i} className="rounded border border-gray-200 bg-white p-3">
                <div className="text-xs font-medium text-smae-body">{tc.metric.name}</div>
                <MetricComparison metric={tc.metric} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Coupling patterns */}
      {event.coupling_patterns.length > 0 && (
        <div>
          <h2 className="mb-2 text-xs font-bold uppercase text-smae-dark-blue">
            Structural Coupling Patterns
          </h2>
          <div className="flex flex-wrap gap-1">
            {event.coupling_patterns.map((p) => (
              <span
                key={p}
                className="rounded bg-amber-100 px-2 py-0.5 text-xs text-smae-dark-amber"
              >
                {COUPLING_PATTERN_LABELS[p] ?? `Pattern ${p}`}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Resistance */}
      <div>
        <h2 className="mb-1 text-xs font-bold uppercase text-smae-dark-green">
          Resistance
        </h2>
        <p
          className={`text-sm italic ${
            hasResistance ? "text-smae-dark-green" : "text-smae-source"
          }`}
        >
          {event.resistance_summary ?? "No resistance data available."}
        </p>
      </div>

      {/* Governance */}
      {event.governance_context && (
        <div>
          <h2 className="mb-1 text-xs font-bold uppercase text-smae-dark-blue">
            Governance Context
          </h2>
          <p className="text-sm text-smae-body">{event.governance_context}</p>
        </div>
      )}

      {/* 30-day Outlook */}
      {event.outlook_30d && (
        <div>
          <h2 className="mb-1 text-xs font-bold uppercase text-smae-dark-blue">
            30-Day Outlook
          </h2>
          <p className="text-sm text-smae-body">{event.outlook_30d}</p>
        </div>
      )}

      {/* Sources */}
      {event.sources.length > 0 && (
        <div>
          <h2 className="mb-2 text-xs font-bold uppercase text-smae-dark-blue">
            Sources
          </h2>
          <ol className="list-inside list-decimal space-y-1 text-xs text-smae-source">
            {event.sources.map((src, i) => (
              <li key={i}>
                {src.organization} — {src.report_name}
                {src.doi && <span className="ml-1">({src.doi})</span>}
                <span className="ml-1">[Tier {src.tier}]</span>
                {src.provisional && (
                  <span className="ml-1 text-smae-dark-amber">[provisional]</span>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

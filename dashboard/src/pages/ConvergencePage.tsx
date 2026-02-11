import { useEvents } from "../api/events";
import { useConvergenceMatrix } from "../api/convergence";
import HeatmapMatrix from "../components/convergence/HeatmapMatrix";
import SystemicNodesTable from "../components/convergence/SystemicNodesTable";
import CouplingPatterns from "../components/convergence/CouplingPatterns";
import Spinner from "../components/shared/Spinner";

export default function ConvergencePage() {
  const { data: eventsData, isLoading: eventsLoading } = useEvents({ limit: 200 });
  const { data: matrix, isLoading: matrixLoading } = useConvergenceMatrix();

  if (eventsLoading || matrixLoading) return <Spinner />;

  const events = eventsData?.items ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-bold text-smae-title">Convergence Analysis</h1>
      <p className="text-xs text-smae-source">
        Multi-network interaction analysis. Convergence nodes reveal where
        metabolic networks intersect — the highest-value analytical targets.
      </p>

      {/* Heatmap */}
      {matrix && <HeatmapMatrix data={matrix} />}

      {/* Systemic nodes */}
      <div>
        <h2 className="mb-2 text-sm font-bold text-smae-dark-amber">
          Systemic Nodes (CI {"\u2265"} 4)
        </h2>
        <SystemicNodesTable events={events} />
      </div>

      {/* Coupling patterns */}
      <CouplingPatterns events={events} />
    </div>
  );
}

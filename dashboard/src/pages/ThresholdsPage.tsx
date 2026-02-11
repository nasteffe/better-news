import { useThresholdDefinitions, useThresholdStatus } from "../api/thresholds";
import ThresholdGrid from "../components/thresholds/ThresholdGrid";
import ThresholdGauge from "../components/thresholds/ThresholdGauge";
import Spinner from "../components/shared/Spinner";

export default function ThresholdsPage() {
  const { data: definitions, isLoading: defsLoading } = useThresholdDefinitions();
  const { data: status, isLoading: statusLoading } = useThresholdStatus();

  if (defsLoading || statusLoading) return <Spinner />;

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-bold text-smae-title">Threshold Monitor</h1>
      <p className="text-xs text-smae-source">
        25 analytical thresholds across absolute, rate-of-change, relational,
        and governance decay categories.
      </p>

      {/* Active crossings */}
      {status && status.length > 0 && (
        <div>
          <h2 className="mb-2 text-sm font-bold text-smae-dark-red">
            Active Threshold Crossings
          </h2>
          <div className="grid gap-2 md:grid-cols-2">
            {status.map((s, i) => (
              <ThresholdGauge key={i} entry={s} />
            ))}
          </div>
        </div>
      )}

      {/* All definitions */}
      {definitions && (
        <div>
          <h2 className="mb-2 text-sm font-bold text-smae-dark-blue">
            All Threshold Definitions
          </h2>
          <ThresholdGrid definitions={definitions} />
        </div>
      )}
    </div>
  );
}

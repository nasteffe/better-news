import { usePipelineStatus, useTriggerPipeline } from "../../api/pipeline";

export default function Header() {
  const { data: status } = usePipelineStatus();
  const trigger = useTriggerPipeline();

  const pipelineLabel =
    status && "status" in status
      ? status.status === "running"
        ? "Pipeline running..."
        : status.status === "completed"
          ? `Last run: ${String(status.events_ingested ?? 0)} events`
          : status.status === "no_runs"
            ? "No pipeline runs"
            : `Pipeline: ${String(status.status)}`
      : "Loading...";

  return (
    <header className="flex h-12 items-center justify-between border-b border-gray-200 bg-white px-6">
      <div className="text-sm text-smae-subhead">{pipelineLabel}</div>
      <button
        onClick={() => trigger.mutate(2)}
        disabled={trigger.isPending}
        className="rounded bg-smae-dark-blue px-3 py-1.5 text-xs font-medium text-white hover:bg-smae-dark-blue/90 disabled:opacity-50"
      >
        {trigger.isPending ? "Starting..." : "Run Pipeline"}
      </button>
    </header>
  );
}

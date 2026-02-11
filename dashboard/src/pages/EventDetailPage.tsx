import { useParams, Link } from "react-router-dom";
import { useEvent } from "../api/events";
import { useGenerateFlashAlert } from "../api/reports";
import EventDetail from "../components/events/EventDetail";
import Spinner from "../components/shared/Spinner";

export default function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: event, isLoading, error } = useEvent(id ?? "");
  const flashAlert = useGenerateFlashAlert();

  if (isLoading) return <Spinner />;
  if (error || !event) {
    return (
      <div className="p-8 text-center">
        <p className="text-sm text-smae-dark-red">Event not found.</p>
        <Link to="/events" className="text-xs text-smae-dark-blue hover:underline">
          Back to events
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <Link to="/events" className="text-xs text-smae-dark-blue hover:underline">
          {"\u2190"} Back to events
        </Link>
        <button
          onClick={() => flashAlert.mutate(event.id)}
          disabled={flashAlert.isPending}
          className="rounded bg-smae-dark-red px-3 py-1.5 text-xs font-medium text-white hover:bg-smae-dark-red/90 disabled:opacity-50"
        >
          {flashAlert.isPending ? "Generating..." : "Generate Flash Alert PDF"}
        </button>
      </div>
      {flashAlert.data && (
        <div className="mb-4 rounded border border-green-200 bg-green-50 px-3 py-2 text-xs text-smae-dark-green">
          Flash alert generated:{" "}
          <a
            href={`/api/v1/reports/download/${flashAlert.data.filename}`}
            className="underline"
          >
            {flashAlert.data.filename}
          </a>
        </div>
      )}
      <EventDetail event={event} />
    </div>
  );
}

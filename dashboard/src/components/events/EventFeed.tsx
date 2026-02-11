import type { Event } from "../../types/smae";
import EventCard from "./EventCard";

export default function EventFeed({ events }: { events: Event[] }) {
  if (events.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-smae-source">
        No events found. Run the pipeline to ingest data.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
    </div>
  );
}

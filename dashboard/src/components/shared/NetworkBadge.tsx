import { NETWORK_LABELS, NETWORK_ROMAN } from "../../types/smae";

export default function NetworkBadge({ id }: { id: number }) {
  return (
    <span className="inline-block rounded bg-smae-dark-blue px-2 py-0.5 text-xs font-medium text-white mr-1 mb-1">
      {NETWORK_ROMAN[id]}: {NETWORK_LABELS[id]}
    </span>
  );
}

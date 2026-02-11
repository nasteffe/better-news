import type { ConvergenceMatrix } from "../../types/smae";

export default function HeatmapMatrix({ data }: { data: ConvergenceMatrix }) {
  const max = Math.max(...data.matrix.flat(), 1);

  const cellColor = (val: number) => {
    if (val === 0) return "bg-gray-50";
    const intensity = Math.round((val / max) * 4);
    const levels = [
      "bg-amber-100",
      "bg-amber-200",
      "bg-amber-300",
      "bg-amber-400",
      "bg-amber-600",
    ];
    return levels[Math.min(intensity, 4)] ?? "bg-amber-100";
  };

  const shortLabels = data.labels.map((_l, i) =>
    ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"][i] ?? ""
  );

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-bold text-smae-dark-amber">
        Network Co-occurrence Matrix
      </h3>
      <table className="text-xs">
        <thead>
          <tr>
            <th className="p-1" />
            {shortLabels.map((l, i) => (
              <th key={i} className="p-1 text-center font-medium text-smae-dark-blue">
                {l}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.matrix.map((row, i) => (
            <tr key={i}>
              <td className="p-1 text-right font-medium text-smae-dark-blue">
                {shortLabels[i]}
              </td>
              {row.map((val, j) => (
                <td
                  key={j}
                  className={`p-1 text-center ${cellColor(val)} ${
                    val > 0 ? "text-smae-body font-medium" : "text-gray-300"
                  }`}
                  title={`${data.labels[i]} x ${data.labels[j]}: ${val}`}
                  style={{ minWidth: "2rem" }}
                >
                  {val}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

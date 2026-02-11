import { useReports } from "../api/reports";
import ReportGenerator from "../components/reports/ReportGenerator";
import ReportArchive from "../components/reports/ReportArchive";
import Spinner from "../components/shared/Spinner";

export default function ReportsPage() {
  const { data: reports, isLoading } = useReports();

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-bold text-smae-title">Reports</h1>
      <p className="text-xs text-smae-source">
        Generate PDF intelligence products: daily briefings, flash alerts,
        and convergence reports.
      </p>
      <ReportGenerator />

      <div>
        <h2 className="mb-2 text-sm font-bold text-smae-dark-blue">
          Report Archive
        </h2>
        {isLoading ? <Spinner /> : <ReportArchive reports={reports ?? []} />}
      </div>
    </div>
  );
}

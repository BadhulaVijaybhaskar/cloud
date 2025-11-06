// pages/integration.js
import { useEffect, useState } from "react";

export default function IntegrationDashboard() {
  const [report, setReport] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const resp = await fetch("/reports/k6/k6_compatibility_report.json");
        if (!resp.ok) throw new Error("report not found");
        const j = await resp.json();
        setReport(j);
      } catch (e) {
        setReport({ error: true, message: String(e) });
      }
    }
    load();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Integration Dashboard — K.6</h1>
      <section className="mb-6">
        <h2 className="text-xl font-semibold">Summary</h2>
        {report === null && <p>Loading report...</p>}
        {report && report.error && <p className="text-red-500">{report.message}</p>}
        {report && !report.error && (
          <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto">
            {JSON.stringify(report, null, 2)}
          </pre>
        )}
      </section>

      <section>
        <h2 className="text-xl font-semibold">Quick Actions</h2>
        <div className="space-x-2 mt-2">
          <button className="px-3 py-2 rounded bg-slate-700 text-white">Re-run Contract Tests</button>
          <button className="px-3 py-2 rounded border">Open Reports Folder</button>
        </div>
        <p className="text-sm text-gray-500 mt-2">Note: Actions require backend endpoints to be wired (SIMULATION_MODE=true allowed).</p>
      </section>
    </div>
  );
}
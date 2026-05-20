import { api } from "@/lib/api";
import { NewIcpForm } from "./new-icp-form";
import { RunPipelineButton } from "./run-pipeline-button";

export default async function IcpsPage() {
  const [icps, buyers] = await Promise.all([
    api.listIcps().catch(() => []),
    api.listBuyers().catch(() => []),
  ]);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Ideal Customer Profiles</h1>
        <p className="text-sm text-slate-500">
          Define who you're selling to. Then run the agents to discover leads.
        </p>
      </header>

      <section className="rounded-lg border bg-white">
        <table className="w-full text-sm">
          <thead className="border-b bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Name</th>
              <th className="px-4 py-2">Industry</th>
              <th className="px-4 py-2">Size</th>
              <th className="px-4 py-2">Geography</th>
              <th className="px-4 py-2">Keywords</th>
              <th className="px-4 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {icps.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                  No ICPs yet — create one below.
                </td>
              </tr>
            )}
            {icps.map((icp) => (
              <tr key={icp.id} className="border-b last:border-0">
                <td className="px-4 py-3 font-medium">{icp.name}</td>
                <td className="px-4 py-3 text-slate-600">{icp.industry || "—"}</td>
                <td className="px-4 py-3 text-slate-600">{icp.company_size || "—"}</td>
                <td className="px-4 py-3 text-slate-600">{icp.geography || "—"}</td>
                <td className="px-4 py-3 text-slate-600">
                  {(icp.keywords || []).join(", ") || "—"}
                </td>
                <td className="px-4 py-3 text-right">
                  <RunPipelineButton icpId={icp.id} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="rounded-lg border bg-white p-5">
        <h2 className="mb-3 text-base font-semibold">Create a new ICP</h2>
        <NewIcpForm buyers={buyers} />
      </section>
    </div>
  );
}

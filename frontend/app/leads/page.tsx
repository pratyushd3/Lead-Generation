import Link from "next/link";
import { api } from "@/lib/api";
import { ScoreBadge, StatusBadge } from "@/components/badges";

export default async function LeadsPage({
  searchParams,
}: {
  searchParams: { icp_id?: string; min_score?: string };
}) {
  const params: { icp_id?: number; min_score?: number } = {};
  if (searchParams.icp_id) params.icp_id = Number(searchParams.icp_id);
  if (searchParams.min_score) params.min_score = Number(searchParams.min_score);

  const [leads, icps] = await Promise.all([
    api.listLeads(params).catch(() => []),
    api.listIcps().catch(() => []),
  ]);

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Leads</h1>
          <p className="text-sm text-slate-500">{leads.length} total</p>
        </div>
      </header>

      <form className="flex flex-wrap items-end gap-3 rounded-lg border bg-white p-4">
        <label className="flex flex-col gap-1">
          <span className="text-xs font-medium text-slate-600">ICP</span>
          <select
            name="icp_id"
            defaultValue={searchParams.icp_id || ""}
            className="rounded border border-slate-300 bg-white px-3 py-1.5 text-sm"
          >
            <option value="">All</option>
            {icps.map((i) => (
              <option key={i.id} value={i.id}>
                {i.name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-xs font-medium text-slate-600">Min score</span>
          <input
            name="min_score"
            type="number"
            min={0}
            max={100}
            defaultValue={searchParams.min_score || ""}
            className="w-28 rounded border border-slate-300 bg-white px-3 py-1.5 text-sm"
          />
        </label>
        <button
          type="submit"
          className="rounded bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-800"
        >
          Filter
        </button>
      </form>

      <section className="rounded-lg border bg-white">
        <table className="w-full text-sm">
          <thead className="border-b bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Score</th>
              <th className="px-4 py-2">Company</th>
              <th className="px-4 py-2">Industry</th>
              <th className="px-4 py-2">Contact</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {leads.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                  No leads match.
                </td>
              </tr>
            )}
            {leads.map((l) => (
              <tr key={l.id} className="border-b last:border-0">
                <td className="px-4 py-3">
                  <ScoreBadge score={l.score} />
                </td>
                <td className="px-4 py-3 font-medium">{l.company_name}</td>
                <td className="px-4 py-3 text-slate-600">{l.industry || "—"}</td>
                <td className="px-4 py-3 text-slate-600">
                  {l.contact_name ? `${l.contact_name}` : "—"}
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={l.status} />
                </td>
                <td className="px-4 py-3 text-right">
                  <Link
                    href={`/leads/${l.id}`}
                    className="text-blue-600 hover:underline"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

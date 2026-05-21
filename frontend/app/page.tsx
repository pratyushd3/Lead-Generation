import Link from "next/link";
import { api, fmtMoney } from "../lib/api";
import { StatusBadge } from "../components/badges";

export default async function DashboardPage() {
  const [icps, leads, orders] = await Promise.all([
    api.listIcps().catch(() => []),
    api.listLeads().catch(() => []),
    api.listOrders().catch(() => []),
  ]);

  const byStatus = leads.reduce<Record<string, number>>((acc, l) => {
    acc[l.status] = (acc[l.status] || 0) + 1;
    return acc;
  }, {});

  const revenue = orders
    .filter((o) => o.payment_status === "paid")
    .reduce((sum, o) => sum + o.price_cents, 0);

  return (
    <div className="space-y-8">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-sm text-slate-500">
            Overview of your ICPs, lead pipeline, and marketplace orders.
          </p>
        </div>
      </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <Stat label="ICPs" value={icps.length} href="/icps" />
        <Stat label="Leads" value={leads.length} href="/leads" />
        <Stat
          label="Orders"
          value={orders.length}
          href="/marketplace"
          sub={`${orders.filter((o) => o.payment_status === "paid").length} paid`}
        />
        <Stat label="Revenue" value={fmtMoney(revenue)} href="/marketplace" />
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Leads by status
        </h2>
        <div className="flex flex-wrap gap-2 rounded-lg border bg-white p-4">
          {Object.keys(byStatus).length === 0 ? (
            <p className="text-sm text-slate-500">
              No leads yet.{" "}
              <Link href="/icps" className="text-blue-600 hover:underline">
                Run the pipeline for an ICP
              </Link>
              .
            </p>
          ) : (
            Object.entries(byStatus).map(([s, n]) => (
              <span key={s} className="flex items-center gap-1.5 text-sm">
                <StatusBadge status={s} />
                <span className="tabular-nums text-slate-600">{n}</span>
              </span>
            ))
          )}
        </div>
      </section>
    </div>
  );
}

function Stat({
  label,
  value,
  sub,
  href,
}: {
  label: string;
  value: string | number;
  sub?: string;
  href?: string;
}) {
  const inner = (
    <div className="rounded-lg border bg-white p-4 transition hover:border-slate-300">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold tabular-nums">{value}</div>
      {sub && <div className="text-xs text-slate-500">{sub}</div>}
    </div>
  );
  return href ? <Link href={href}>{inner}</Link> : inner;
}

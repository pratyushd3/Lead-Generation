import Link from "next/link";
import { api, fmtMoney, priceForScore } from "@/lib/api";
import { ScoreBadge, StatusBadge } from "@/components/badges";
import { BuyButton } from "./buy-button";

export default async function MarketplacePage() {
  const [leads, buyers, orders] = await Promise.all([
    api.listLeads({ min_score: 50 }).catch(() => []),
    api.listBuyers().catch(() => []),
    api.listOrders().catch(() => []),
  ]);

  const available = leads.filter((l) => l.status !== "sold");
  const sold = leads.filter((l) => l.status === "sold");
  const defaultBuyerId = buyers[0]?.id;

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Marketplace</h1>
        <p className="text-sm text-slate-500">
          Browse qualified leads and unlock contact + outreach drafts on purchase.
        </p>
      </header>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Available leads ({available.length})
        </h2>
        <div className="rounded-lg border bg-white">
          <table className="w-full text-sm">
            <thead className="border-b bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-2">Score</th>
                <th className="px-4 py-2">Company</th>
                <th className="px-4 py-2">Industry</th>
                <th className="px-4 py-2">Price</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {available.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                    No leads available. Run the pipeline for an ICP first.
                  </td>
                </tr>
              )}
              {available.map((l) => (
                <tr key={l.id} className="border-b last:border-0">
                  <td className="px-4 py-3"><ScoreBadge score={l.score} /></td>
                  <td className="px-4 py-3 font-medium">
                    <Link href={`/leads/${l.id}`} className="hover:underline">
                      {l.company_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{l.industry || "—"}</td>
                  <td className="px-4 py-3 tabular-nums">
                    {fmtMoney(priceForScore(l.score))}
                  </td>
                  <td className="px-4 py-3"><StatusBadge status={l.status} /></td>
                  <td className="px-4 py-3 text-right">
                    {defaultBuyerId ? (
                      <BuyButton leadId={l.id} buyerId={defaultBuyerId} />
                    ) : (
                      <span className="text-xs text-slate-400">no buyer</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Recent orders
        </h2>
        <div className="rounded-lg border bg-white">
          <table className="w-full text-sm">
            <thead className="border-b bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-2">Order</th>
                <th className="px-4 py-2">Lead</th>
                <th className="px-4 py-2">Price</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Provider</th>
              </tr>
            </thead>
            <tbody>
              {orders.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                    No orders yet.
                  </td>
                </tr>
              )}
              {orders.map((o) => (
                <tr key={o.id} className="border-b last:border-0">
                  <td className="px-4 py-3 tabular-nums">#{o.id}</td>
                  <td className="px-4 py-3">
                    <Link href={`/leads/${o.lead_id}`} className="text-blue-600 hover:underline">
                      Lead #{o.lead_id}
                    </Link>
                  </td>
                  <td className="px-4 py-3 tabular-nums">{fmtMoney(o.price_cents)}</td>
                  <td className="px-4 py-3"><StatusBadge status={o.payment_status} /></td>
                  <td className="px-4 py-3 text-slate-600">{o.payment_provider || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {sold.length > 0 && (
          <p className="mt-3 text-xs text-slate-400">{sold.length} sold lead(s) hidden from available.</p>
        )}
      </section>
    </div>
  );
}

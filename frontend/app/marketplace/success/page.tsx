import Link from "next/link";

export default function SuccessPage({
  searchParams,
}: {
  searchParams: { order_id?: string; session_id?: string };
}) {
  return (
    <div className="mx-auto max-w-md rounded-lg border bg-white p-8 text-center">
      <div className="text-3xl">✓</div>
      <h1 className="mt-2 text-xl font-semibold">Purchase complete</h1>
      <p className="mt-1 text-sm text-slate-500">
        {searchParams.order_id ? `Order #${searchParams.order_id}.` : ""} Your
        lead is now unlocked with full contact details and outreach drafts.
      </p>
      <div className="mt-6 flex justify-center gap-3">
        <Link
          href="/marketplace"
          className="rounded border border-slate-300 bg-white px-4 py-1.5 text-sm font-medium hover:bg-slate-50"
        >
          Back to marketplace
        </Link>
        <Link
          href="/leads"
          className="rounded bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-800"
        >
          View leads
        </Link>
      </div>
    </div>
  );
}

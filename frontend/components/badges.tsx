const STATUS_COLORS: Record<string, string> = {
  new: "bg-slate-100 text-slate-700",
  enriched: "bg-slate-100 text-slate-700",
  scored: "bg-slate-100 text-slate-700",
  ready: "bg-blue-100 text-blue-800",
  sent: "bg-amber-100 text-amber-800",
  delivered: "bg-amber-100 text-amber-800",
  opened: "bg-purple-100 text-purple-800",
  replied: "bg-emerald-100 text-emerald-800",
  bounced: "bg-red-100 text-red-800",
  sold: "bg-emerald-200 text-emerald-900",
  pending: "bg-slate-100 text-slate-700",
  paid: "bg-emerald-100 text-emerald-800",
};

export function StatusBadge({ status }: { status: string }) {
  const cls = STATUS_COLORS[status] || "bg-slate-100 text-slate-700";
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}

export function ScoreBadge({ score }: { score: number | null | undefined }) {
  if (score == null) return <span className="text-slate-400 text-xs">—</span>;
  const cls =
    score >= 85
      ? "bg-emerald-100 text-emerald-800"
      : score >= 70
      ? "bg-blue-100 text-blue-800"
      : score >= 50
      ? "bg-amber-100 text-amber-800"
      : "bg-slate-100 text-slate-700";
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-semibold tabular-nums ${cls}`}>
      {score.toFixed(0)}
    </span>
  );
}

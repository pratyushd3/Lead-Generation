import Link from "next/link";
import { api } from "../../../lib/api";
import { ScoreBadge, StatusBadge } from "../../../components/badges";
import { SendOutreachButton } from "./send-outreach-button";

export default async function LeadDetailPage({ params }: { params: { id: string } }) {
  const lead = await api.getLead(Number(params.id)).catch(() => null);
  if (!lead) {
    return (
      <div className="text-sm text-slate-500">
        Lead not found. <Link href="/leads" className="text-blue-600 hover:underline">Back to leads</Link>
      </div>
    );
  }

  const enrichment = (lead.enrichment || {}) as Record<string, unknown>;
  const tech = (enrichment.tech_stack as string[]) || [];
  const signals = (enrichment.buying_signals as string[]) || [];

  return (
    <div className="space-y-6">
      <Link href="/leads" className="text-sm text-slate-500 hover:underline">
        ← All leads
      </Link>

      <header className="flex items-start justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold tracking-tight">
              {lead.company_name}
            </h1>
            <ScoreBadge score={lead.score} />
            <StatusBadge status={lead.status} />
          </div>
          <p className="text-sm text-slate-500">
            {lead.industry || "—"} · {lead.employee_count ?? "?"} ppl ·{" "}
            {lead.location || "—"}
          </p>
          {lead.website && (
            <a
              href={lead.website}
              target="_blank"
              rel="noreferrer"
              className="text-sm text-blue-600 hover:underline"
            >
              {lead.website}
            </a>
          )}
        </div>
      </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card title="Contact">
          <KV label="Name" value={lead.contact_name} />
          <KV label="Title" value={lead.contact_title} />
          <KV label="Email" value={lead.contact_email} />
        </Card>
        <Card title="Score reasoning">
          <p className="text-sm text-slate-700">{lead.score_reasoning || "—"}</p>
        </Card>
        <Card title="Tech stack">
          <Tags tags={tech} />
        </Card>
        <Card title="Buying signals">
          <Tags tags={signals} />
        </Card>
      </section>

      <section className="rounded-lg border bg-white p-5">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-base font-semibold">Outreach</h2>
          <SendOutreachButton leadId={lead.id} hasEmail={!!lead.contact_email} />
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <EmailDraft title="First touch" body={lead.outreach_email} />
          <EmailDraft title="Follow-up" body={lead.outreach_followup} />
        </div>

        <div className="mt-4 flex flex-wrap gap-3 text-xs text-slate-500">
          {lead.sent_at && <span>sent: {fmtDate(lead.sent_at)}</span>}
          {lead.delivered_at && <span>delivered: {fmtDate(lead.delivered_at)}</span>}
          {lead.opened_at && <span>opened: {fmtDate(lead.opened_at)}</span>}
          {lead.replied_at && <span>replied: {fmtDate(lead.replied_at)}</span>}
          {lead.bounced_at && <span className="text-red-600">bounced: {fmtDate(lead.bounced_at)}</span>}
        </div>
      </section>
    </div>
  );
}

function fmtDate(s: string) {
  return new Date(s).toLocaleString();
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </h3>
      <div className="space-y-1 text-sm">{children}</div>
    </div>
  );
}

function KV({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div className="flex justify-between gap-3 text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="font-medium">{value || "—"}</span>
    </div>
  );
}

function Tags({ tags }: { tags: string[] }) {
  if (!tags.length) return <p className="text-sm text-slate-400">—</p>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {tags.map((t) => (
        <span
          key={t}
          className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-700"
        >
          {t}
        </span>
      ))}
    </div>
  );
}

function EmailDraft({ title, body }: { title: string; body: string | null | undefined }) {
  return (
    <div className="rounded border bg-slate-50 p-3">
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </h4>
      <pre className="whitespace-pre-wrap text-xs text-slate-800">{body || "—"}</pre>
    </div>
  );
}

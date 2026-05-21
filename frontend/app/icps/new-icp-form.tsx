"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import type { Buyer } from "../../lib/types";

export function NewIcpForm({ buyers }: { buyers: Buyer[] }) {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(formData: FormData) {
    setSubmitting(true);
    setError(null);
    try {
      const buyerId = Number(formData.get("buyer_id"));
      const keywords = String(formData.get("keywords") || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      await api.createIcp({
        buyer_id: buyerId,
        name: String(formData.get("name") || ""),
        industry: String(formData.get("industry") || "") || null,
        company_size: String(formData.get("company_size") || "") || null,
        geography: String(formData.get("geography") || "") || null,
        pain_points: String(formData.get("pain_points") || "") || null,
        keywords,
      });
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form action={onSubmit} className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Field label="Buyer">
        <select name="buyer_id" required className={inputCls}>
          {buyers.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Name">
        <input name="name" required className={inputCls} placeholder="e.g. Mid-market RevOps" />
      </Field>
      <Field label="Industry">
        <input name="industry" className={inputCls} placeholder="SaaS" />
      </Field>
      <Field label="Company size">
        <input name="company_size" className={inputCls} placeholder="11-200" />
      </Field>
      <Field label="Geography">
        <input name="geography" className={inputCls} placeholder="North America" />
      </Field>
      <Field label="Keywords (comma-separated)">
        <input name="keywords" className={inputCls} placeholder="analytics, revenue, SaaS" />
      </Field>
      <Field label="Pain points" full>
        <textarea name="pain_points" className={inputCls} rows={2} />
      </Field>

      <div className="sm:col-span-2 flex items-center gap-3">
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
        >
          {submitting ? "Creating…" : "Create ICP"}
        </button>
        {error && <span className="text-sm text-red-600">{error}</span>}
      </div>
    </form>
  );
}

const inputCls =
  "w-full rounded border border-slate-300 bg-white px-3 py-1.5 text-sm focus:border-slate-500 focus:outline-none";

function Field({
  label,
  children,
  full,
}: {
  label: string;
  children: React.ReactNode;
  full?: boolean;
}) {
  return (
    <label className={`flex flex-col gap-1 ${full ? "sm:col-span-2" : ""}`}>
      <span className="text-xs font-medium text-slate-600">{label}</span>
      {children}
    </label>
  );
}

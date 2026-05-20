"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export function SendOutreachButton({
  leadId,
  hasEmail,
}: {
  leadId: number;
  hasEmail: boolean;
}) {
  const router = useRouter();
  const [sending, setSending] = useState<"email" | "followup" | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  async function send(useFollowup: boolean) {
    setSending(useFollowup ? "followup" : "email");
    setMsg(null);
    try {
      await api.sendOutreach(leadId, useFollowup);
      setMsg(useFollowup ? "Follow-up sent" : "Email sent");
      router.refresh();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Send failed");
    } finally {
      setSending(null);
    }
  }

  return (
    <div className="flex items-center gap-2">
      {msg && <span className="text-xs text-slate-500">{msg}</span>}
      <button
        onClick={() => send(false)}
        disabled={!hasEmail || sending !== null}
        className="rounded bg-slate-900 px-3 py-1 text-xs font-medium text-white hover:bg-slate-800 disabled:opacity-50"
      >
        {sending === "email" ? "Sending…" : "Send email"}
      </button>
      <button
        onClick={() => send(true)}
        disabled={!hasEmail || sending !== null}
        className="rounded border border-slate-300 bg-white px-3 py-1 text-xs font-medium hover:bg-slate-50 disabled:opacity-50"
      >
        {sending === "followup" ? "Sending…" : "Send follow-up"}
      </button>
    </div>
  );
}

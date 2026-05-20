"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export function RunPipelineButton({ icpId }: { icpId: number }) {
  const router = useRouter();
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function run() {
    setRunning(true);
    setMsg(null);
    try {
      const leads = await api.runPipeline(icpId, 5);
      setMsg(`Generated ${leads.length} leads`);
      router.refresh();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="flex items-center gap-2 justify-end">
      {msg && <span className="text-xs text-slate-500">{msg}</span>}
      <button
        onClick={run}
        disabled={running}
        className="rounded border border-slate-300 bg-white px-3 py-1 text-xs font-medium hover:bg-slate-50 disabled:opacity-50"
      >
        {running ? "Running…" : "Run pipeline"}
      </button>
    </div>
  );
}

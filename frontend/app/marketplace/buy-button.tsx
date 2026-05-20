"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export function BuyButton({ leadId, buyerId }: { leadId: number; buyerId: number }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function buy() {
    setBusy(true);
    setErr(null);
    try {
      const res = await api.checkout(buyerId, leadId);
      // For Stripe, redirect to the hosted checkout URL.
      // For mock, the URL points to /marketplace/success and the order is
      // already paid server-side.
      if (res.url && res.provider === "stripe") {
        window.location.href = res.url;
        return;
      }
      router.push(`/marketplace/success?order_id=${res.order_id}`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Purchase failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex items-center justify-end gap-2">
      {err && <span className="text-xs text-red-600">{err}</span>}
      <button
        onClick={buy}
        disabled={busy}
        className="rounded bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
      >
        {busy ? "Processing…" : "Buy"}
      </button>
    </div>
  );
}

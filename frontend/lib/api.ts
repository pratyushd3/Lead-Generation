import type {
  Buyer,
  CheckoutResponse,
  ICP,
  Lead,
  LeadFull,
  Order,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(
  path: string,
  init: RequestInit = {},
  cache: RequestCache = "no-store"
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    cache,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listBuyers: () => request<Buyer[]>("/buyers"),
  listIcps: () => request<ICP[]>("/icps"),
  createIcp: (body: Omit<ICP, "id">) =>
    request<ICP>("/icps", { method: "POST", body: JSON.stringify(body) }),

  runPipeline: (icp_id: number, max_leads = 5) =>
    request<Lead[]>("/pipeline/run", {
      method: "POST",
      body: JSON.stringify({ icp_id, max_leads }),
    }),

  listLeads: (params: { icp_id?: number; min_score?: number } = {}) => {
    const q = new URLSearchParams();
    if (params.icp_id !== undefined) q.set("icp_id", String(params.icp_id));
    if (params.min_score !== undefined) q.set("min_score", String(params.min_score));
    const qs = q.toString();
    return request<Lead[]>(`/leads${qs ? `?${qs}` : ""}`);
  },
  getLead: (id: number) => request<LeadFull>(`/leads/${id}`),
  sendOutreach: (id: number, useFollowup = false) =>
    request<LeadFull>(`/leads/${id}/send`, {
      method: "POST",
      body: JSON.stringify({ use_followup: useFollowup }),
    }),

  listOrders: () => request<Order[]>("/marketplace/orders"),
  checkout: (buyer_id: number, lead_id: number) =>
    request<CheckoutResponse>("/marketplace/checkout", {
      method: "POST",
      body: JSON.stringify({ buyer_id, lead_id }),
    }),
};

export const fmtMoney = (cents: number) => `$${(cents / 100).toFixed(2)}`;

export const priceForScore = (score: number | null | undefined) => {
  if (score == null) return 1000;
  if (score >= 85) return 5000;
  if (score >= 70) return 3000;
  if (score >= 50) return 1500;
  return 500;
};

/**
 * Simple in-memory database for Vercel deployment.
 * Data persists across requests in dev mode (hot reload keeps the module alive)
 * but resets on cold starts in production. For persistent storage, swap this
 * with Vercel Postgres or any external DB.
 */

export type Buyer = { id: number; name: string; email: string; created_at: string };
export type ICP = {
  id: number;
  buyer_id: number;
  name: string;
  industry: string | null;
  company_size: string | null;
  geography: string | null;
  pain_points: string | null;
  keywords: string[];
};
export type Lead = {
  id: number;
  icp_id: number;
  company_name: string;
  website: string | null;
  industry: string | null;
  employee_count: number | null;
  location: string | null;
  contact_name: string | null;
  contact_title: string | null;
  contact_email: string | null;
  enrichment: Record<string, unknown> | null;
  score: number | null;
  score_reasoning: string | null;
  outreach_email: string | null;
  outreach_followup: string | null;
  message_id: string | null;
  sent_at: string | null;
  delivered_at: string | null;
  opened_at: string | null;
  replied_at: string | null;
  bounced_at: string | null;
  status: string;
  created_at: string;
};
export type Order = {
  id: number;
  buyer_id: number;
  lead_id: number;
  price_cents: number;
  payment_status: string;
  payment_provider: string | null;
  paid_at: string | null;
  created_at: string;
};

// In-memory store (survives hot reloads in dev via globalThis)
interface DB {
  buyers: Buyer[];
  icps: ICP[];
  leads: Lead[];
  orders: Order[];
  nextId: { buyer: number; icp: number; lead: number; order: number };
}

const globalKey = "__leadgen_db__";

function createDB(): DB {
  return {
    buyers: [
      { id: 1, name: "Pipeline Pro Agency", email: "ops@pipelinepro.example", created_at: new Date().toISOString() },
    ],
    icps: [
      {
        id: 1, buyer_id: 1, name: "Mid-market SaaS RevOps", industry: "SaaS",
        company_size: "11-200", geography: "North America",
        pain_points: "fragmented revenue data, slow lead-to-cash cycles",
        keywords: ["analytics", "revenue", "SaaS"],
      },
      {
        id: 2, buyer_id: 1, name: "Logistics ops modernization", industry: "Logistics",
        company_size: "50-500", geography: "US",
        pain_points: "manual dispatch, fragmented carrier data",
        keywords: ["logistics", "operations", "automation"],
      },
    ],
    leads: [],
    orders: [],
    nextId: { buyer: 2, icp: 3, lead: 1, order: 1 },
  };
}

function getDB(): DB {
  if (!(globalThis as any)[globalKey]) {
    (globalThis as any)[globalKey] = createDB();
  }
  return (globalThis as any)[globalKey];
}

export const db = {
  get: getDB,

  addBuyer(name: string, email: string): Buyer {
    const store = getDB();
    const buyer: Buyer = { id: store.nextId.buyer++, name, email, created_at: new Date().toISOString() };
    store.buyers.push(buyer);
    return buyer;
  },

  addIcp(data: Omit<ICP, "id">): ICP {
    const store = getDB();
    const icp: ICP = { id: store.nextId.icp++, ...data };
    store.icps.push(icp);
    return icp;
  },

  addLead(data: Omit<Lead, "id" | "created_at">): Lead {
    const store = getDB();
    const lead: Lead = { id: store.nextId.lead++, ...data, created_at: new Date().toISOString() };
    store.leads.push(lead);
    return lead;
  },

  addOrder(data: Omit<Order, "id" | "created_at">): Order {
    const store = getDB();
    const order: Order = { id: store.nextId.order++, ...data, created_at: new Date().toISOString() };
    store.orders.push(order);
    return order;
  },

  findLead(id: number): Lead | undefined {
    return getDB().leads.find((l) => l.id === id);
  },

  findIcp(id: number): ICP | undefined {
    return getDB().icps.find((i) => i.id === id);
  },

  findBuyer(id: number): Buyer | undefined {
    return getDB().buyers.find((b) => b.id === id);
  },
};

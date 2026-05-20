export type Buyer = { id: number; name: string; email: string };

export type ICP = {
  id: number;
  buyer_id: number;
  name: string;
  industry?: string | null;
  company_size?: string | null;
  geography?: string | null;
  pain_points?: string | null;
  keywords: string[];
};

export type Lead = {
  id: number;
  icp_id: number;
  company_name: string;
  website?: string | null;
  industry?: string | null;
  employee_count?: number | null;
  location?: string | null;
  contact_name?: string | null;
  contact_title?: string | null;
  contact_email?: string | null;
  score?: number | null;
  score_reasoning?: string | null;
  status: string;
};

export type LeadFull = Lead & {
  enrichment?: Record<string, unknown> | null;
  outreach_email?: string | null;
  outreach_followup?: string | null;
  message_id?: string | null;
  sent_at?: string | null;
  delivered_at?: string | null;
  opened_at?: string | null;
  replied_at?: string | null;
  bounced_at?: string | null;
};

export type Order = {
  id: number;
  buyer_id: number;
  lead_id: number;
  price_cents: number;
  payment_status: string;
  payment_provider?: string | null;
  paid_at?: string | null;
  created_at: string;
};

export type CheckoutResponse = {
  order_id: number;
  session_id: string | null;
  url: string | null;
  payment_status: string;
  provider: string;
};

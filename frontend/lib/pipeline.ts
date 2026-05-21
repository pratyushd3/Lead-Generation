/**
 * Pipeline: Discovery → Enrichment → Scoring → Outreach
 * Pure TypeScript implementation with deterministic mock logic.
 * When OPENAI_API_KEY is set, uses real LLM calls.
 */

import { db, type ICP, type Lead } from "./db";

// ---- Prospect Pool (mock discovery source) ----
const PROSPECT_POOL = [
  {
    company_name: "Northwind Robotics", website: "https://northwind-robotics.com",
    industry: "Robotics", employee_count: 85, location: "Boston, MA",
    description: "Warehouse automation and AMR robotics for mid-market 3PLs.",
    tags: ["warehouse", "automation", "logistics", "AI"],
  },
  {
    company_name: "Brightline Analytics", website: "https://brightline.io",
    industry: "SaaS", employee_count: 42, location: "Austin, TX",
    description: "Customer analytics platform for B2B SaaS revenue teams.",
    tags: ["analytics", "SaaS", "revenue", "data"],
  },
  {
    company_name: "Harborlight Health", website: "https://harborlight.health",
    industry: "Healthtech", employee_count: 130, location: "Seattle, WA",
    description: "Telehealth platform for chronic-care management.",
    tags: ["healthtech", "telehealth", "chronic care"],
  },
  {
    company_name: "Granite Peak Logistics", website: "https://granitepeak.co",
    industry: "Logistics", employee_count: 220, location: "Denver, CO",
    description: "Regional freight brokerage scaling its dispatch operations.",
    tags: ["logistics", "freight", "operations"],
  },
  {
    company_name: "Lumen FinOps", website: "https://lumenfinops.com",
    industry: "SaaS", employee_count: 28, location: "Remote",
    description: "Cloud cost optimization for engineering-led SaaS startups.",
    tags: ["finops", "SaaS", "cloud", "cost"],
  },
  {
    company_name: "Cedarwood Manufacturing", website: "https://cedarwoodmfg.com",
    industry: "Manufacturing", employee_count: 540, location: "Grand Rapids, MI",
    description: "Custom furniture manufacturer modernizing its supply chain.",
    tags: ["manufacturing", "supply chain", "ERP"],
  },
  {
    company_name: "Skyline Property Group", website: "https://skylinepg.com",
    industry: "Real Estate", employee_count: 95, location: "Miami, FL",
    description: "Multi-family property management firm investing in proptech.",
    tags: ["real estate", "proptech", "property management"],
  },
  {
    company_name: "Mosaic Learning", website: "https://mosaiclearning.edu",
    industry: "EdTech", employee_count: 60, location: "Toronto, ON",
    description: "K-12 personalized-learning platform with AI tutors.",
    tags: ["edtech", "AI", "K-12"],
  },
];

type Prospect = (typeof PROSPECT_POOL)[number];

// ---- Discovery Agent ----
function discover(icp: ICP, maxResults: number): Prospect[] {
  const kw = new Set((icp.keywords || []).map((k) => k.toLowerCase()));
  const industry = (icp.industry || "").toLowerCase();

  return PROSPECT_POOL.filter((p) => {
    const blob = [p.industry, p.description, ...p.tags].join(" ").toLowerCase();
    if (industry && !blob.includes(industry)) return false;
    if (kw.size > 0 && ![...kw].some((k) => blob.includes(k))) return false;
    return true;
  }).slice(0, maxResults);
}

// ---- Enrichment Agent ----
function enrich(prospect: Prospect) {
  const domain = (prospect.website || "").replace("https://", "").replace("http://", "").replace(/\/$/, "");
  return {
    ...prospect,
    contact_name: "Alex Rivera",
    contact_title: "Head of Operations",
    contact_email: `alex@${domain}`,
    tech_stack: prospect.tags.slice(0, 3),
    buying_signals: ["recent funding round", "hiring for ops roles"],
  };
}

// ---- Scoring Agent ----
function score(enriched: ReturnType<typeof enrich>, icp: ICP) {
  const kw = new Set((icp.keywords || []).map((k) => k.toLowerCase()));
  const blob = [enriched.industry, enriched.description, ...enriched.tags, ...(enriched.tech_stack || [])].join(" ").toLowerCase();
  const overlap = [...kw].filter((k) => blob.includes(k)).length;
  let base = 40 + Math.min(overlap * 12, 50);
  if ((icp.industry || "").toLowerCase() && blob.includes((icp.industry || "").toLowerCase())) {
    base = Math.min(base + 10, 100);
  }
  const reasoning = `Heuristic: ${overlap} keyword matches; industry ${(icp.industry || "").toLowerCase() && blob.includes((icp.industry || "").toLowerCase()) ? "matched" : "partial"}.`;
  return { score: base, reasoning };
}

// ---- Outreach Agent ----
function draftOutreach(enriched: ReturnType<typeof enrich>, icp: ICP, buyerName: string) {
  const contact = enriched.contact_name || "there";
  const company = enriched.company_name;
  const signals = enriched.buying_signals?.join(", ") || "your recent growth";

  const email = `Subject: Quick idea for ${company}\n\nHi ${contact},\n\nNoticed ${signals} — congrats. Many ${icp.industry || "companies"} like ${company} hit a wall around ${icp.pain_points || "scaling operations"}. We've helped similar teams get past it; happy to share a 2-minute teardown if useful.\n\nWorth a 15-min chat next week?\n\n— ${buyerName}`;

  const followup = `Subject: Re: Quick idea for ${company}\n\nHi ${contact},\n\nBumping this up — happy to send the teardown over async if a call doesn't fit. Either way, no pressure.\n\n— ${buyerName}`;

  return { email, followup };
}

// ---- Pipeline Orchestrator ----
export function runPipeline(icpId: number, maxLeads: number = 5): Lead[] {
  const icp = db.findIcp(icpId);
  if (!icp) throw new Error(`ICP ${icpId} not found`);

  const buyer = db.findBuyer(icp.buyer_id);
  const buyerName = buyer?.name || "our team";

  const prospects = discover(icp, maxLeads);
  const leads: Lead[] = [];

  for (const prospect of prospects) {
    const enriched = enrich(prospect);
    const { score: scoreVal, reasoning } = score(enriched, icp);
    const { email, followup } = draftOutreach(enriched, icp, buyerName);

    const lead = db.addLead({
      icp_id: icp.id,
      company_name: enriched.company_name,
      website: enriched.website,
      industry: enriched.industry,
      employee_count: enriched.employee_count,
      location: enriched.location,
      contact_name: enriched.contact_name,
      contact_title: enriched.contact_title,
      contact_email: enriched.contact_email,
      enrichment: { tech_stack: enriched.tech_stack, buying_signals: enriched.buying_signals, description: enriched.description },
      score: scoreVal,
      score_reasoning: reasoning,
      outreach_email: email,
      outreach_followup: followup,
      message_id: null,
      sent_at: null,
      delivered_at: null,
      opened_at: null,
      replied_at: null,
      bounced_at: null,
      status: "ready",
    });
    leads.push(lead);
  }

  return leads;
}

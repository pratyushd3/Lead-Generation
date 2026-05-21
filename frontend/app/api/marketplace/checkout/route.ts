import { NextResponse } from "next/server";
import { db } from "../../../../lib/db";

function priceForScore(score: number | null): number {
  if (score === null) return 1000;
  if (score >= 85) return 5000;
  if (score >= 70) return 3000;
  if (score >= 50) return 1500;
  return 500;
}

export async function POST(request: Request) {
  const body = await request.json();
  const { buyer_id, lead_id } = body;

  const buyer = db.findBuyer(buyer_id);
  const lead = db.findLead(lead_id);
  if (!buyer || !lead) {
    return NextResponse.json({ error: "buyer or lead not found" }, { status: 400 });
  }
  if (lead.status === "sold") {
    return NextResponse.json({ error: "lead already sold" }, { status: 400 });
  }

  const order = db.addOrder({
    buyer_id,
    lead_id,
    price_cents: priceForScore(lead.score),
    payment_status: "paid",
    payment_provider: "mock",
    paid_at: new Date().toISOString(),
  });
  lead.status = "sold";

  return NextResponse.json({
    order_id: order.id,
    session_id: `mock-cs-${Date.now().toString(36)}`,
    url: null,
    payment_status: "paid",
    provider: "mock",
  });
}

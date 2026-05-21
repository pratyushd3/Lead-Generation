import { NextResponse } from "next/server";
import { db } from "../../../lib/db";

export async function GET() {
  return NextResponse.json(db.get().icps);
}

export async function POST(request: Request) {
  const body = await request.json();
  if (!body.name || !body.buyer_id) {
    return NextResponse.json({ error: "name and buyer_id required" }, { status: 400 });
  }
  if (!db.findBuyer(body.buyer_id)) {
    return NextResponse.json({ error: "buyer not found" }, { status: 404 });
  }
  const icp = db.addIcp({
    buyer_id: body.buyer_id,
    name: body.name,
    industry: body.industry || null,
    company_size: body.company_size || null,
    geography: body.geography || null,
    pain_points: body.pain_points || null,
    keywords: body.keywords || [],
  });
  return NextResponse.json(icp, { status: 201 });
}

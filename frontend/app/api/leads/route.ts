import { NextResponse } from "next/server";
import { db } from "../../../lib/db";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const icpId = searchParams.get("icp_id");
  const minScore = parseFloat(searchParams.get("min_score") || "0");

  let leads = db.get().leads;
  if (icpId) leads = leads.filter((l) => l.icp_id === Number(icpId));
  if (minScore > 0) leads = leads.filter((l) => (l.score || 0) >= minScore);

  leads.sort((a, b) => (b.score || 0) - (a.score || 0));
  return NextResponse.json(leads);
}

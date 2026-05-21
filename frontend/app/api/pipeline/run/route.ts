import { NextResponse } from "next/server";
import { runPipeline } from "../../../../lib/pipeline";

export async function POST(request: Request) {
  const body = await request.json();
  const icpId = body.icp_id;
  const maxLeads = body.max_leads || 5;

  if (!icpId) {
    return NextResponse.json({ error: "icp_id required" }, { status: 400 });
  }

  try {
    const leads = runPipeline(icpId, maxLeads);
    return NextResponse.json(leads);
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message }, { status: 404 });
  }
}

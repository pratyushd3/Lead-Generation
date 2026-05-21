import { NextResponse } from "next/server";
import { db } from "../../../../../lib/db";

export async function POST(request: Request, { params }: { params: { id: string } }) {
  const lead = db.findLead(Number(params.id));
  if (!lead) {
    return NextResponse.json({ error: "lead not found" }, { status: 404 });
  }
  if (!lead.contact_email) {
    return NextResponse.json({ error: "lead has no contact_email" }, { status: 400 });
  }

  const body = await request.json();
  const useFollowup = body.use_followup || false;
  const raw = useFollowup ? lead.outreach_followup : lead.outreach_email;
  if (!raw) {
    return NextResponse.json({ error: "no outreach draft available" }, { status: 400 });
  }

  // Mock send
  lead.message_id = `mock-${Date.now().toString(36)}`;
  lead.sent_at = new Date().toISOString();
  lead.status = "sent";

  return NextResponse.json(lead);
}

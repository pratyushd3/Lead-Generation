import { NextResponse } from "next/server";
import { db } from "../../../../lib/db";

export async function GET(_request: Request, { params }: { params: { id: string } }) {
  const lead = db.findLead(Number(params.id));
  if (!lead) {
    return NextResponse.json({ error: "lead not found" }, { status: 404 });
  }
  return NextResponse.json(lead);
}

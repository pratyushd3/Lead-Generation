import { NextResponse } from "next/server";
import { db } from "../../../lib/db";

export async function GET() {
  return NextResponse.json(db.get().buyers);
}

export async function POST(request: Request) {
  const body = await request.json();
  if (!body.name || !body.email) {
    return NextResponse.json({ error: "name and email required" }, { status: 400 });
  }
  const buyer = db.addBuyer(body.name, body.email);
  return NextResponse.json(buyer, { status: 201 });
}

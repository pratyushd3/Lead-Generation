import { NextResponse } from "next/server";
import { db } from "../../../../lib/db";

export async function GET() {
  const orders = [...db.get().orders].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  return NextResponse.json(orders);
}

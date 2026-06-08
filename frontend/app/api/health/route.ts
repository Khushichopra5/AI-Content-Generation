import { NextResponse } from "next/server";

import { API_BASE_URL } from "@/lib/config";

export async function GET() {
  const upstream = `${API_BASE_URL.replace(/\/$/, "")}/health/`;

  try {
    const response = await fetch(upstream, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      cache: "no-store",
    });

    const payload = await response.json().catch(() => ({}));

    return NextResponse.json(payload, {
      status: response.status,
    });
  } catch {
    return NextResponse.json(
      {
        status: "error",
        database: false,
        redis: false,
        debug: false,
      },
      { status: 502 },
    );
  }
}

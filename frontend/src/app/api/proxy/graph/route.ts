import { NextResponse } from 'next/server';

const API_BASE = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const res = await fetch(`${API_BASE}/api/graph`, {
      cache: 'no-store',
    });
    if (!res.ok) {
      return NextResponse.json(
        { error: `Backend responded with ${res.status}` },
        { status: res.status }
      );
    }
    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: `Failed to reach backend at ${API_BASE}` },
      { status: 503 }
    );
  }
}

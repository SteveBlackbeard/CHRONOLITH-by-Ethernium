import { NextResponse } from 'next/server';
import { getEvents } from '@/lib/eventChain';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const events = await getEvents(10);
    return NextResponse.json({ events });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

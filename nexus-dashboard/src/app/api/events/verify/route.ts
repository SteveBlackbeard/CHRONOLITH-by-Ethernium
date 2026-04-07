import { NextResponse } from 'next/server';
import { verifyChain } from '@/lib/eventChain';

export const dynamic = 'force-dynamic';

export async function POST() {
  try {
    const result = await verifyChain();
    return NextResponse.json(result);
  } catch (error: any) {
    return NextResponse.json({ intact: false, error: error.message }, { status: 500 });
  }
}

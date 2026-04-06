import { NextResponse } from 'next/server';
import { readFileSync } from 'fs';
import { join } from 'path';

export async function GET() {
  try {
    // Read STATE.json from the repository root (one level up from nexus-dashboard)
    const statePath = join(process.cwd(), '..', 'STATE.json');
    const raw = readFileSync(statePath, 'utf-8');
    const state = JSON.parse(raw);
    return NextResponse.json(state);
  } catch (error) {
    return NextResponse.json({
      merkle_root: "error_reading_state",
      last_check: new Date().toISOString(),
      physics: { H: 0, H_max: 0, eta: 0, N: 0, W: 0, gini: 0 },
      drift_kl: 0,
      crystallizer_version: "3.0.0",
    }, { status: 500 });
  }
}

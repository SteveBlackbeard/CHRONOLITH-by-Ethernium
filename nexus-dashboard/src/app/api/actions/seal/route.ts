import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { join } from 'path';
import { promisify } from 'util';
import { appendEvent } from '@/lib/eventChain';

const execPromise = promisify(exec);

export async function POST() {
  try {
    const scriptPath = join(process.cwd(), '..', '.github', 'scripts', 'setup_guardian.py');
    const rootPath = join(process.cwd(), '..');

    console.log(`[SOVEREIGN] Launching Guardian Seal: ${scriptPath}`);

    const { stdout, stderr } = await execPromise(`python "${scriptPath}"`, { cwd: rootPath });

    if (stderr && !stderr.includes('warning')) {
      return NextResponse.json({ success: false, error: stderr }, { status: 500 });
    }

    await appendEvent('SEAL_VAULT', { action: 'Seal Installed' });

    return NextResponse.json({ 
      success: true, 
      message: "Vault Sealed Successfully",
      output: stdout 
    });

  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

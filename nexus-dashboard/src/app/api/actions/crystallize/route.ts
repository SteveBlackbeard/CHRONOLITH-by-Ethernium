import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { join } from 'path';
import { promisify } from 'util';
import { appendEvent } from '@/lib/eventChain';

const execPromise = promisify(exec);

export async function POST() {
  try {
    // Path to the crystallization script
    // process.cwd() is nexus-dashboard root.
    const scriptPath = join(process.cwd(), '..', '.github', 'scripts', 'crystalize.py');
    const rootPath = join(process.cwd(), '..');

    console.log(`[SOVEREIGN] Launching DNA Crystallization: ${scriptPath}`);

    // Execute the python script from the repository root context
    const { stdout, stderr } = await execPromise(`python "${scriptPath}"`, { cwd: rootPath });

    if (stderr && !stderr.includes('warning')) {
      console.error(`[SOVEREIGN] ERR: ${stderr}`);
      return NextResponse.json({ success: false, error: stderr }, { status: 500 });
    }

    // Determine payload or summary if possible
    const payload = { action: 'Crystallization', status: 'Success' };
    await appendEvent('CRYSTALLIZE', payload);

    return NextResponse.json({ 
      success: true, 
      message: "DNA Crystallization Successful",
      output: stdout 
    });

  } catch (error: any) {
    console.error(`[SOVEREIGN] EXECUTION FAILED: ${error.message}`);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

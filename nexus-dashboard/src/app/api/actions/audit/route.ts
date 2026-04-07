import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { join } from 'path';
import { promisify } from 'util';

const execPromise = promisify(exec);

export async function POST() {
  try {
    const scriptPath = join(process.cwd(), '..', '.github', 'scripts', 'audit_comparison.py');
    const rootPath = join(process.cwd(), '..');

    console.log(`[SOVEREIGN] Launching System Audit: ${scriptPath}`);

    const { stdout, stderr } = await execPromise(`python "${scriptPath}"`, { cwd: rootPath });

    if (stderr && !stderr.includes('warning')) {
      return NextResponse.json({ success: false, error: stderr }, { status: 500 });
    }

    return NextResponse.json({ 
      success: true, 
      message: "System Audit Complete",
      output: stdout 
    });

  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

import { NextResponse } from 'next/server';
import { readdirSync, statSync } from 'fs';
import { join } from 'path';

export async function POST(request: Request) {
  try {
    const { projectPath } = await request.json();

    if (!projectPath) {
      return NextResponse.json({ success: false, error: 'No project path provided' }, { status: 400 });
    }

    const entries: { name: string; type: 'file' | 'dir'; size?: number }[] = [];
    const EXCLUDE = ['.git', 'node_modules', '__pycache__', '.pytest_cache', '.venv', 'dist', '.next', '.egg-info'];

    try {
      const items = readdirSync(projectPath);
      for (const item of items) {
        if (EXCLUDE.some(ex => item.includes(ex))) continue;
        if (item.startsWith('.')) continue;

        const fullPath = join(projectPath, item);
        try {
          const stats = statSync(fullPath);
          entries.push({
            name: item,
            type: stats.isDirectory() ? 'dir' : 'file',
            size: stats.isDirectory() ? undefined : stats.size,
          });
        } catch {
          // Skip inaccessible files
        }
      }
    } catch (err: any) {
      return NextResponse.json({ success: false, error: `Cannot read directory: ${err.message}` }, { status: 500 });
    }

    return NextResponse.json({ success: true, entries });

  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

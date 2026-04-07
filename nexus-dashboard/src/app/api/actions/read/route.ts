import { NextResponse } from 'next/server';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

export async function POST(request: Request) {
  try {
    const { filePath } = await request.json();

    if (!filePath) {
      return NextResponse.json({ success: false, error: 'No file path provided' }, { status: 400 });
    }

    // Resolve the file path relative to the repository root
    const rootPath = join(process.cwd(), '..');
    const fullPath = join(rootPath, filePath);

    if (!existsSync(fullPath)) {
      return NextResponse.json({ success: false, error: `File not found: ${filePath}` }, { status: 404 });
    }

    // Only read text-based files
    const textExtensions = ['.md', '.json', '.py', '.ts', '.tsx', '.yml', '.yaml', '.toml', '.txt', '.css', '.js', '.html', '.ps1'];
    const ext = filePath.substring(filePath.lastIndexOf('.'));
    
    if (!textExtensions.includes(ext.toLowerCase())) {
      return NextResponse.json({ success: false, error: `Binary file type not supported: ${ext}` }, { status: 400 });
    }

    const content = readFileSync(fullPath, 'utf-8');

    return NextResponse.json({
      success: true,
      fileName: filePath.split('/').pop() || filePath.split('\\').pop() || filePath,
      content: content.substring(0, 10000), // Cap at 10k chars for performance
      truncated: content.length > 10000,
    });

  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

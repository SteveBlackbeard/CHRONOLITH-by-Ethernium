import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import { extname, join } from 'path';

export const runtime = 'nodejs';

const overrideAssetDir = join(process.cwd(), 'public', 'assets', 'nodes', 'overrides');

function getContentType(fileName: string) {
  const ext = extname(fileName).toLowerCase();
  if (ext === '.glb') return 'model/gltf-binary';
  if (ext === '.gltf') return 'model/gltf+json';
  return 'application/octet-stream';
}

export async function GET(
  _request: Request,
  context: { params: Promise<{ fileName: string }> | { fileName: string } },
) {
  try {
    const params = await Promise.resolve(context.params);
    const fileName = decodeURIComponent(params.fileName || '');
    if (!fileName || fileName.includes('/') || fileName.includes('\\') || fileName.includes('..')) {
      return NextResponse.json({ success: false, error: 'Invalid asset path' }, { status: 400 });
    }

    const absolutePath = join(overrideAssetDir, fileName);
    const buffer = await fs.readFile(absolutePath);
    return new NextResponse(buffer, {
      headers: {
        'Content-Type': getContentType(fileName),
        'Cache-Control': 'no-store',
      },
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error?.message || 'ASSET_NOT_FOUND' }, { status: 404 });
  }
}

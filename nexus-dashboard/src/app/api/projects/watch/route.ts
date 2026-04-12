import { NextRequest, NextResponse } from 'next/server';
import chokidar from 'chokidar';
import fs from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const encoder = new TextEncoder();
  const searchParams = req.nextUrl.searchParams;
  const projectPath = searchParams.get('path');

  if (!projectPath) {
    return new NextResponse('Missing project path', { status: 400 });
  }

  const stream = new ReadableStream({
    start(controller) {
      // Create relative path for chokidar
      const absolutePath = path.resolve(process.cwd(), '..', projectPath);
      
      console.log(`[SOVEREIGN_WATCHER] Initializing on: ${absolutePath}`);

      const watcher = chokidar.watch(absolutePath, {
        persistent: true,
        ignoreInitial: true,
        depth: 1, // Only watch top-level for performance
      });

      const sendEvent = (event: string, data: any) => {
        const payload = `data: ${JSON.stringify({ event, ...data })}\n\n`;
        controller.enqueue(encoder.encode(payload));
      };

      watcher
        .on('add', (filePath) => sendEvent('add', { 
          name: path.basename(filePath), 
          type: 'file' 
        }))
        .on('addDir', (dirPath) => sendEvent('add', { 
          name: path.basename(dirPath), 
          type: 'dir' 
        }))
        .on('unlink', (filePath) => sendEvent('unlink', { 
          name: path.basename(filePath) 
        }))
        .on('unlinkDir', (dirPath) => sendEvent('unlink', { 
          name: path.basename(dirPath) 
        }))
        .on('change', (filePath) => sendEvent('change', { 
          name: path.basename(filePath) 
        }));

      // Keep connection alive with a heartbeat
      const heartbeat = setInterval(() => {
        controller.enqueue(encoder.encode(': heartbeat\n\n'));
      }, 15000);

      req.signal.addEventListener('abort', () => {
        console.log(`[SOVEREIGN_WATCHER] Closing watcher for: ${projectPath}`);
        clearInterval(heartbeat);
        watcher.close();
        controller.close();
      });
    },
  });

  return new NextResponse(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
    },
  });
}

import { NextRequest } from 'next/server';
import chokidar from 'chokidar';
import { join } from 'path';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const rootPath = join(process.cwd(), '..');
  
  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();
      
      const sendEvent = (event: string, data: any) => {
        try {
          controller.enqueue(encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`));
        } catch (e) {
          // Stream might have closed
        }
      };
      
      // Sending an initial connection event
      sendEvent('connected', { status: 'Synaptic Link Active' });

      // Heartbeat 
      const heartbeat = setInterval(() => {
        sendEvent('ping', { time: Date.now() });
      }, 5000);

      // We watch common code files, excluding hidden files, node_modules, and the dashboard itself
      // to avoid recursive loops when the dashboard compiles or updates its own state.
      const watcher = chokidar.watch([
        '**/*.py',
        '**/*.md',
        '**/*.json',
        '**/*.txt'
      ], {
        cwd: rootPath,
        ignored: [
          /(^|[\/\\])\../,     // dotfiles (like .git, .github)
          /node_modules/,      // deps
          /nexus-dashboard/,   // dashboard directory itself
          /__pycache__/        // python cache
        ],
        persistent: true,
        ignoreInitial: true,
      });

      watcher.on('all', (event, path) => {
        // Broadcast the file event
        sendEvent('file-change', { event, path });
      });

      req.signal.addEventListener('abort', () => {
        clearInterval(heartbeat);
        watcher.close();
      });
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
    },
  });
}

import { NextResponse } from 'next/server';
import { forwardBridgePayload, getAdapterStatuses, getAdapterConfig, invokeOllamaChat } from '@/lib/localAdapters';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function resolveProvider(input?: string | null) {
  const raw = (input || process.env.CONTINUITY_CHAT_PROVIDER || 'openclaw').toLowerCase().trim();
  if (raw === 'ollama') return 'ollama' as const;
  if (raw === 'moltbot') return 'moltbot' as const;
  return 'openclaw' as const;
}

export async function GET() {
  const provider = resolveProvider();
  return NextResponse.json({
    success: true,
    provider,
    adapters: getAdapterStatuses(),
    ready: getAdapterConfig(provider).enabled && Boolean(getAdapterConfig(provider).baseUrl),
  });
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const provider = resolveProvider(body?.provider);
    const prompt = String(body?.prompt || '').trim();

    if (!prompt) {
      return NextResponse.json({ success: false, error: 'Missing prompt' }, { status: 400 });
    }

    if (provider === 'ollama') {
      const result = await invokeOllamaChat([
        {
          role: 'system',
          content:
            'You are Clawdbot operating inside Continuity Legacy. Be concise, operational, and use local tool-calling emulation when available.',
        },
        { role: 'user', content: prompt },
      ]);

      return NextResponse.json({
        success: true,
        provider,
        reply:
          result?.message?.content ||
          result?.response ||
          result?.content ||
          'NO_RESPONSE',
        raw: result,
      });
    }

    const result = await forwardBridgePayload(
      provider,
      {
        prompt,
        source: 'continuity-legacy-dashboard',
        toolCalling: 'emulated',
      },
      '',
    );

    return NextResponse.json({
      success: true,
      provider,
      reply:
        result?.reply ||
        result?.message ||
        result?.content ||
        result?.text ||
        JSON.stringify(result),
      raw: result,
    });
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error?.message || 'CHAT_BRIDGE_FAILURE' },
      { status: 500 },
    );
  }
}

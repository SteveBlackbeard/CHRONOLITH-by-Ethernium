type AdapterProvider = 'ollama' | 'openclaw' | 'moltbot';

type AdapterConfig = {
  enabled: boolean;
  baseUrl: string | null;
  model?: string | null;
  apiKey?: string | null;
  timeoutMs: number;
};

export type AdapterStatus = {
  provider: AdapterProvider;
  enabled: boolean;
  configured: boolean;
  baseUrl: string | null;
  model?: string | null;
  hasApiKey: boolean;
};

export type OllamaChatMessage = {
  role: 'system' | 'user' | 'assistant';
  content: string;
};

function readBool(value: string | undefined, fallback = false) {
  if (!value) return fallback;
  return ['1', 'true', 'yes', 'on'].includes(value.toLowerCase());
}

function readInt(value: string | undefined, fallback: number) {
  const parsed = Number.parseInt(value || '', 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function normalizeUrl(value: string | undefined) {
  if (!value) return null;
  const trimmed = value.trim();
  return trimmed ? trimmed.replace(/\/+$/, '') : null;
}

export function getAdapterConfig(provider: AdapterProvider): AdapterConfig {
  if (provider === 'ollama') {
    return {
      enabled: readBool(process.env.CONTINUITY_OLLAMA_ENABLED, true),
      baseUrl: normalizeUrl(process.env.CONTINUITY_OLLAMA_BASE_URL) || 'http://127.0.0.1:11434',
      model: process.env.CONTINUITY_OLLAMA_MODEL || 'llama3.1',
      timeoutMs: readInt(process.env.CONTINUITY_OLLAMA_TIMEOUT_MS, 45000),
    };
  }

  if (provider === 'openclaw') {
    return {
      enabled: readBool(process.env.CONTINUITY_OPENCLAW_ENABLED, false),
      baseUrl: normalizeUrl(process.env.CONTINUITY_OPENCLAW_BASE_URL),
      apiKey: process.env.CONTINUITY_OPENCLAW_API_KEY || null,
      timeoutMs: readInt(process.env.CONTINUITY_OPENCLAW_TIMEOUT_MS, 45000),
    };
  }

  return {
    enabled: readBool(process.env.CONTINUITY_MOLTBOT_ENABLED, false),
    baseUrl: normalizeUrl(process.env.CONTINUITY_MOLTBOT_BASE_URL),
    apiKey: process.env.CONTINUITY_MOLTBOT_API_KEY || null,
    timeoutMs: readInt(process.env.CONTINUITY_MOLTBOT_TIMEOUT_MS, 45000),
  };
}

export function getAdapterStatuses(): AdapterStatus[] {
  return (['ollama', 'openclaw', 'moltbot'] as AdapterProvider[]).map((provider) => {
    const config = getAdapterConfig(provider);
    return {
      provider,
      enabled: config.enabled,
      configured: Boolean(config.baseUrl),
      baseUrl: config.baseUrl,
      model: config.model || null,
      hasApiKey: Boolean(config.apiKey),
    };
  });
}

function buildTimeoutSignal(timeoutMs: number) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  return {
    signal: controller.signal,
    dispose: () => clearTimeout(timer),
  };
}

export async function invokeOllamaChat(messages: OllamaChatMessage[]) {
  const config = getAdapterConfig('ollama');
  if (!config.enabled || !config.baseUrl) {
    throw new Error('OLLAMA_ADAPTER_NOT_ENABLED');
  }

  const timeout = buildTimeoutSignal(config.timeoutMs);
  try {
    const response = await fetch(`${config.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: config.model,
        stream: false,
        messages,
      }),
      signal: timeout.signal,
    });

    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload?.error || `OLLAMA_HTTP_${response.status}`);
    }
    return payload;
  } finally {
    timeout.dispose();
  }
}

export async function forwardBridgePayload(provider: 'openclaw' | 'moltbot', payload: unknown, path?: string) {
  const config = getAdapterConfig(provider);
  if (!config.enabled || !config.baseUrl) {
    throw new Error(`${provider.toUpperCase()}_ADAPTER_NOT_ENABLED`);
  }

  const timeout = buildTimeoutSignal(config.timeoutMs);
  try {
    const response = await fetch(`${config.baseUrl}${path || ''}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey ? { Authorization: `Bearer ${config.apiKey}` } : {}),
      },
      body: JSON.stringify(payload || {}),
      signal: timeout.signal,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data?.error || `${provider.toUpperCase()}_HTTP_${response.status}`);
    }
    return data;
  } finally {
    timeout.dispose();
  }
}

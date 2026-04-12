import { ScannedEntry } from './graphData';

const EXCLUDE_NAMES = ['.git', 'node_modules', '__pycache__', '.pytest_cache', '.venv', 'dist', '.next', '.egg-info'];
const handleRegistry = new Map<string, FileSystemDirectoryHandle>();

type IterableDirectoryHandle = FileSystemDirectoryHandle & {
  values(): AsyncIterable<FileSystemHandle>;
};

function shouldSkipEntry(name: string) {
  if (name.startsWith('.')) return true;
  return EXCLUDE_NAMES.some((entry) => name.includes(entry));
}

export function registerLinkedSystemHandle(systemId: string, handle: FileSystemDirectoryHandle) {
  handleRegistry.set(systemId, handle);
}

export function removeLinkedSystemHandle(systemId: string) {
  handleRegistry.delete(systemId);
}

export function getLinkedSystemHandle(systemId: string) {
  return handleRegistry.get(systemId) || null;
}

export async function listTopLevelEntriesFromHandle(handle: FileSystemDirectoryHandle): Promise<ScannedEntry[]> {
  const entries: ScannedEntry[] = [];
  const iterableHandle = handle as IterableDirectoryHandle;

  for await (const entry of iterableHandle.values()) {
    const name = entry.name;
    if (shouldSkipEntry(name)) continue;

    if (entry.kind === 'directory') {
      entries.push({ name, type: 'dir' });
      continue;
    }

    let size: number | undefined;
    try {
      size = (await (entry as FileSystemFileHandle).getFile()).size;
    } catch {
      size = undefined;
    }

    entries.push({ name, type: 'file', size });
  }

  return entries.sort((left, right) => {
    if (left.type !== right.type) return left.type === 'dir' ? -1 : 1;
    return left.name.localeCompare(right.name);
  });
}

export async function readHandleBackedFile(systemId: string, relativeFilePath: string) {
  const directoryHandle = getLinkedSystemHandle(systemId);
  if (!directoryHandle) {
    throw new Error('FILESYSTEM_HANDLE_UNAVAILABLE');
  }

  const normalizedPath = relativeFilePath.replace(/\\/g, '/').replace(/^\/+/, '');
  const pathSegments = normalizedPath.split('/').filter(Boolean);

  if (pathSegments.length !== 1) {
    throw new Error('HANDLE_READ_DEPTH_UNSUPPORTED');
  }

  const fileHandle = await directoryHandle.getFileHandle(pathSegments[0]);
  const file = await fileHandle.getFile();
  const content = await file.text();

  return {
    fileName: file.name,
    content: content.slice(0, 10000),
    truncated: content.length > 10000,
  };
}

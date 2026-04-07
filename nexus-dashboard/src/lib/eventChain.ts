import { promises as fs } from 'fs';
import { join } from 'path';
import crypto from 'crypto';

export interface ChainEvent {
  seq: number;
  type: string;
  timestamp: string;
  input_hash: string;
  output_hash: string;
  parent_hash: string;
  payload: any;
  chain_hash: string;
}

const CHAIN_FILE = join(process.cwd(), '..', 'EVENT_CHAIN.jsonl');
const STATE_FILE = join(process.cwd(), '..', 'STATE.json');

function computeHash(data: string): string {
  return crypto.createHash('sha256').update(data).digest('hex');
}

async function getStateHash(): Promise<string> {
  try {
    const stateStr = await fs.readFile(STATE_FILE, 'utf-8');
    return computeHash(stateStr.trim());
  } catch {
    return '0'.repeat(64);
  }
}

export async function appendEvent(type: string, payload: any): Promise<ChainEvent> {
  let seq = 0;
  let parent_hash = '0'.repeat(64);
  let previous_output_hash = '0'.repeat(64);
  
  try {
    const content = await fs.readFile(CHAIN_FILE, 'utf-8');
    const lines = content.trim().split('\n').filter(Boolean);
    if (lines.length > 0) {
      const lastEvent = JSON.parse(lines[lines.length - 1]) as ChainEvent;
      seq = lastEvent.seq + 1;
      parent_hash = lastEvent.chain_hash;
      previous_output_hash = lastEvent.output_hash;
    }
  } catch (e) {
    // File doesn't exist or is empty
  }

  const timestamp = new Date().toISOString();
  const output_hash = await getStateHash();

  const eventCore = {
    seq,
    type,
    timestamp,
    input_hash: seq === 0 ? output_hash : previous_output_hash,
    output_hash,
    parent_hash,
    payload
  };

  // Ensure consistent property ordering for JSON hashing
  const deterministicStr = JSON.stringify(eventCore, Object.keys(eventCore).sort());
  const chain_hash = computeHash(deterministicStr);

  const newEvent: ChainEvent = { ...eventCore, chain_hash };

  await fs.appendFile(CHAIN_FILE, JSON.stringify(newEvent) + '\n', 'utf-8');
  return newEvent;
}

export async function verifyChain(): Promise<{ intact: boolean; error?: string }> {
  try {
    const content = await fs.readFile(CHAIN_FILE, 'utf-8');
    const lines = content.trim().split('\n').filter(Boolean);
    
    let expectedParentHash = '0'.repeat(64);
    
    for (let i = 0; i < lines.length; i++) {
      const event = JSON.parse(lines[i]) as ChainEvent;
      
      if (event.seq !== i) return { intact: false, error: `Sequence mismatch at seq ${i}` };
      if (event.parent_hash !== expectedParentHash) return { intact: false, error: `Chain broken at seq ${i}` };
      
      const { chain_hash, ...core } = event;
      const deterministicStr = JSON.stringify(core, Object.keys(core).sort());
      const computed = computeHash(deterministicStr);
      
      if (computed !== chain_hash) return { intact: false, error: `Hash tampered at seq ${i}` };
      
      expectedParentHash = chain_hash;
    }
    
    return { intact: true };
  } catch (e: any) {
    if (e.code === 'ENOENT') return { intact: true }; // Empty is intact
    return { intact: false, error: e.message };
  }
}

export async function getEvents(limit = 10): Promise<ChainEvent[]> {
  try {
    const content = await fs.readFile(CHAIN_FILE, 'utf-8');
    const lines = content.trim().split('\n').filter(Boolean);
    const events = lines.map(l => JSON.parse(l)).reverse().slice(0, limit);
    return events;
  } catch (e) {
    return [];
  }
}

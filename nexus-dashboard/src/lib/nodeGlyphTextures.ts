import * as THREE from 'three';

export type DocumentGlyphKind = 'generic' | 'python' | 'json' | 'markdown' | 'folder';

const glyphTextureCache = new Map<string, THREE.CanvasTexture>();

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number,
) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function strokeLine(
  ctx: CanvasRenderingContext2D,
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  width: number,
  color: string,
  alpha = 1,
) {
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.lineWidth = width;
  ctx.lineCap = 'round';
  ctx.strokeStyle = color;
  ctx.globalAlpha = alpha;
  ctx.stroke();
  ctx.globalAlpha = 1;
}

export function createNodeGlyphTexture(kind: DocumentGlyphKind, accent: string) {
  const safeAccent = accent || '#ffffff';
  const cacheKey = `${kind}:${safeAccent}`;
  const existing = glyphTextureCache.get(cacheKey);
  if (existing) return existing;

  const canvas = document.createElement('canvas');
  canvas.width = 160;
  canvas.height = 160;
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    const texture = new THREE.Texture();
    glyphTextureCache.set(cacheKey, texture as THREE.CanvasTexture);
    return texture as THREE.CanvasTexture;
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.shadowColor = safeAccent;
  ctx.shadowBlur = 18;

  if (kind === 'folder') {
    ctx.strokeStyle = safeAccent;
    ctx.fillStyle = 'rgba(255,255,255,0.08)';

    roundRect(ctx, 26, 52, 108, 68, 14);
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(32, 52);
    ctx.lineTo(70, 52);
    ctx.lineTo(86, 34);
    ctx.lineTo(122, 34);
    ctx.quadraticCurveTo(132, 34, 132, 44);
    ctx.lineTo(132, 52);
    ctx.closePath();
    ctx.fillStyle = 'rgba(255,255,255,0.12)';
    ctx.fill();
    ctx.stroke();

    strokeLine(ctx, 48, 78, 104, 78, 8, '#67e8f9', 0.95);
    strokeLine(ctx, 48, 94, 92, 94, 6, '#ffffff', 0.76);
  } else {
    ctx.strokeStyle = safeAccent;
    ctx.fillStyle = 'rgba(255,255,255,0.08)';
    roundRect(ctx, 34, 18, 92, 122, 14);
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(94, 18);
    ctx.lineTo(126, 50);
    ctx.lineTo(94, 50);
    ctx.closePath();
    ctx.fillStyle = 'rgba(255,255,255,0.14)';
    ctx.fill();
    ctx.stroke();

    if (kind === 'python') {
      ctx.fillStyle = '#67e8f9';
      roundRect(ctx, 50, 42, 40, 28, 8);
      ctx.fill();
      ctx.fillStyle = '#f59e0b';
      roundRect(ctx, 70, 74, 40, 28, 8);
      ctx.fill();
      ctx.fillStyle = '#020617';
      ctx.beginPath();
      ctx.arc(82, 54, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(78, 88, 4, 0, Math.PI * 2);
      ctx.fill();
    } else if (kind === 'json') {
      strokeLine(ctx, 56, 46, 56, 110, 5, '#67e8f9', 0.95);
      strokeLine(ctx, 104, 46, 104, 110, 5, '#67e8f9', 0.95);
      strokeLine(ctx, 70, 58, 90, 58, 5, '#ffffff', 0.86);
      strokeLine(ctx, 70, 80, 90, 80, 5, '#ffffff', 0.72);
      strokeLine(ctx, 70, 102, 90, 102, 5, '#ffffff', 0.6);
      ctx.fillStyle = '#22d3ee';
      [58, 80, 102].forEach((y) => {
        ctx.beginPath();
        ctx.arc(80, y, 4, 0, Math.PI * 2);
        ctx.fill();
      });
    } else if (kind === 'markdown') {
      ctx.fillStyle = '#ffffff';
      roundRect(ctx, 50, 46, 54, 9, 4);
      ctx.fill();
      ctx.fillStyle = '#67e8f9';
      roundRect(ctx, 50, 64, 38, 8, 4);
      ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,0.82)';
      roundRect(ctx, 50, 81, 48, 8, 4);
      ctx.fill();
      strokeLine(ctx, 50, 108, 66, 94, 5, '#22d3ee', 0.95);
      strokeLine(ctx, 66, 94, 80, 104, 5, '#22d3ee', 0.95);
      strokeLine(ctx, 80, 104, 102, 76, 5, '#22d3ee', 0.95);
    } else {
      ctx.fillStyle = '#ffffff';
      roundRect(ctx, 50, 48, 54, 8, 4);
      ctx.fill();
      ctx.fillStyle = '#67e8f9';
      roundRect(ctx, 50, 66, 42, 8, 4);
      ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,0.82)';
      roundRect(ctx, 50, 84, 48, 8, 4);
      ctx.fill();
      ctx.fillStyle = 'rgba(103,232,249,0.72)';
      roundRect(ctx, 50, 102, 34, 8, 4);
      ctx.fill();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.generateMipmaps = false;
  glyphTextureCache.set(cacheKey, texture);
  return texture;
}

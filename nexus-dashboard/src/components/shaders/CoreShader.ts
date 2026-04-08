import * as THREE from 'three';
import { shaderMaterial } from '@react-three/drei';

// AAA Core Shader Material Class
// Using shaderMaterial from @react-three/drei ensures robust compilation and uniform binding.
export const CoreShaderMaterial = shaderMaterial(
  {
    u_time: 0,
    u_entropy: 1.0,
    u_drift: 0.0,
    u_pulse: 0.0,
    u_baseColor: new THREE.Color('#ffffff'),
    u_isWireframe: 0.0,
    u_intensity: 1.0
  },
  // Vertex Shader
  `
    uniform float u_time;
    uniform float u_entropy;
    uniform float u_drift;
    uniform float u_pulse;

    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec3 vViewPosition;

    void main() {
      vPosition = position;
      
      // Entropy and Drift stabilization logic
      float instability = (1.0 - u_entropy) * 3.0;
      vec3 pos = position;
      
      if (instability > 0.1) {
        float noise = sin(position.x * 20.0 + u_time * 8.0) * cos(position.y * 20.0 + u_time * 8.0);
        pos += normal * noise * instability * 0.05;
      }
      
      // Pulse scaling
      pos += normal * u_pulse * 0.4;

      vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
      vViewPosition = -mvPosition.xyz;
      vNormal = normalize(normalMatrix * normal);
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  // Fragment Shader
  `
    uniform float u_time;
    uniform float u_drift;
    uniform float u_pulse;
    uniform vec3 u_baseColor;
    uniform float u_isWireframe;
    uniform float u_intensity;
    
    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec3 vViewPosition;

    void main() {
      vec3 normal = normalize(vNormal);
      vec3 viewDir = normalize(vViewPosition);

      // Fresnel rim effect
      float dotProduct = max(0.0, dot(normal, viewDir));
      float rim = 1.0 - dotProduct;
      float fresnel = pow(rim, 4.0);
      
      vec3 color = u_baseColor;
      
      // Procedural scanlines
      float scanline = sin(vPosition.y * 80.0 - u_time * 5.0) * 0.05;
      
      // Pulse flash
      color = mix(color, vec3(1.0, 1.0, 1.0), u_pulse);
      
      if (u_isWireframe > 0.5) {
          // Energetic wireframe for AAA Bloom
          gl_FragColor = vec4(color * 3.0 * u_intensity, 1.0);
      } else {
          // Solid glass look
          float alpha = 0.5 + (fresnel * 0.5) + u_pulse + max(0.0, scanline);
          vec3 finalColor = color * (0.6 + fresnel * 0.7 * u_intensity);
          gl_FragColor = vec4(finalColor, min(alpha, 1.0));
      }
    }
  `
);

// AAA Beam Shader Material Class
export const BeamShaderMaterial = shaderMaterial(
  {
    u_time: 0,
    u_color: new THREE.Color('#ffffff')
  },
  // Vertex Shader
  `
    uniform float u_time;
    attribute float aProgress;
    varying float vAlpha;

    void main() {
      float flow = fract(aProgress - u_time * 0.8);
      vAlpha = pow(1.0 - abs(flow - 0.5) * 2.0, 6.0);
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      gl_PointSize = (1.5 + vAlpha * 8.0) * (20.0 / -mvPosition.z);
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  // Fragment Shader
  `
    uniform vec3 u_color;
    varying float vAlpha;
    void main() {
      vec2 coord = gl_PointCoord - vec2(0.5);
      if(length(coord) > 0.5) discard;
      vec3 glow = u_color * (1.0 + vAlpha * 5.0);
      gl_FragColor = vec4(glow, max(0.1, vAlpha * 0.8));
    }
  `
);

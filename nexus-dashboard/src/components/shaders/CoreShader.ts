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
      
      float instability = (1.0 - u_entropy) * 2.4 + u_drift * 1.4;
      vec3 pos = position;
      
      if (instability > 0.1) {
        float waveA = sin(position.x * 5.5 + u_time * 0.9);
        float waveB = cos(position.z * 4.8 - u_time * 0.75);
        float liquid = waveA * waveB;
        pos += normal * liquid * instability * 0.024;
      }
      
      pos += normal * u_pulse * 0.12;

      vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
      vViewPosition = -mvPosition.xyz;
      vNormal = normalize(normalMatrix * normal);
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
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
      float ndv = max(0.0, dot(normal, viewDir));
      float rim = pow(1.0 - ndv, 2.4);
      float specular = pow(max(0.0, dot(reflect(-viewDir, normal), vec3(0.0, 1.0, 0.25))), 12.0);
      float liquidSweep = 0.5 + 0.5 * sin((vPosition.x + vPosition.z) * 4.0 - u_time * 1.8);
      float pulseFactor = u_pulse * 0.55;

      vec3 shadowMetal = u_baseColor * 0.22;
      vec3 bodyMetal = u_baseColor * (0.34 + liquidSweep * 0.08);
      vec3 liquidLight = mix(vec3(0.55), vec3(0.78), liquidSweep) * (0.035 + rim * 0.05 + pulseFactor * 0.03);
      vec3 reflected = vec3(1.0) * (specular * 0.08 + rim * 0.04);
      vec3 finalColor = (shadowMetal + bodyMetal + liquidLight + reflected) * max(0.14, u_intensity);

      if (u_isWireframe > 0.5) {
        float wireAlpha = clamp(0.03 + rim * 0.05 + pulseFactor * 0.02, 0.03, 0.1);
        gl_FragColor = vec4(mix(u_baseColor * 0.76, vec3(0.88), rim * 0.08) * max(0.06, u_intensity), wireAlpha);
      } else {
        float alpha = clamp(0.18 + rim * 0.08 + specular * 0.03 + pulseFactor * 0.02, 0.16, 0.3);
        gl_FragColor = vec4(finalColor, alpha);
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

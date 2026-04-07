import * as THREE from 'three';

export const CoreShaderMaterial = {
  uniforms: {
    u_time: { value: 0 },
    u_entropy: { value: 1.0 }, // eta (balance)
    u_drift: { value: 0.0 }, // KL divergence
    u_pulse: { value: 0.0 }, // 0 to 1 shockwave
    u_baseColor: { value: new THREE.Color('#ffffff') }
  },
  vertexShader: `
    uniform float u_time;
    uniform float u_entropy;
    uniform float u_drift;
    uniform float u_pulse;

    varying vec3 vPosition;
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vViewPosition;

    void main() {
      vUv = uv;
      vPosition = position;

      // Entropy determines geometric stability
      float instability = (1.0 - u_entropy) * 3.0; 
      
      // Drift jitter
      float noise = sin(position.x * 20.0 + u_time * 8.0) * cos(position.y * 20.0 + u_time * 8.0);
      
      vec3 pos = position;
      
      // Ambient distress geometry
      if (instability > 0.1) {
        pos += normal * noise * instability * 0.05;
      }
      if (u_drift > 0.05) {
        pos += normal * sin(u_time * 15.0) * u_drift * 0.3;
      }

      // Pulse shockwave scaling
      pos += normal * u_pulse * 0.4;

      vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
      vViewPosition = -mvPosition.xyz;
      
      // Transform normal safely
      vNormal = normalize(normalMatrix * normal);
      
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  fragmentShader: `
    uniform float u_time;
    uniform float u_drift;
    uniform float u_pulse;
    uniform vec3 u_baseColor;
    
    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec3 vViewPosition;

    void main() {
      vec3 normal = normalize(vNormal);
      vec3 viewDir = normalize(vViewPosition);

      // FRESNEL (RIM SCATTERING LOGIC)
      float dotProduct = max(0.0, dot(normal, viewDir));
      float rim = 1.0 - dotProduct;
      float fresnel = pow(rim, 3.0); // sharp edge glow
      
      vec3 color = u_baseColor;
      
      // PROCEDURAL SCANLINES
      float scanline = sin(vPosition.y * 80.0 - u_time * 10.0) * 0.08;
      
      // DRIFT CONTAMINATION (Shift to Red/Amber)
      if (u_drift > 0.0) {
        float driftMix = min(u_drift * 4.0, 1.0);
        vec3 hazardColor = mix(vec3(1.0, 0.6, 0.0), vec3(1.0, 0.1, 0.2), driftMix);
        color = mix(color, hazardColor, driftMix * abs(sin(u_time * 3.0)));
      }

      // PULSE OVERDRIVE
      vec3 finalColor = mix(color, vec3(1.0, 1.0, 1.0), u_pulse);
      
      // ALPHA CALCULATION (Glass body)
      float alpha = max(0.1, fresnel) + max(0.0, scanline) + (u_pulse * 0.6);
      
      // INTENSITY EMISSION MULTIPLIER
      gl_FragColor = vec4(finalColor * (1.2 + fresnel * 2.5), alpha);
    }
  `
};

export const BeamShaderMaterial = {
  uniforms: {
    u_time: { value: 0 },
    u_color: { value: new THREE.Color('#ffffff') }
  },
  vertexShader: `
    uniform float u_time;
    varying float vAlpha;
    void main() {
      vAlpha = max(0.1, 0.5 + 0.5 * sin(position.x * 5.0 + position.y * 5.0 - u_time * 5.0));
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      gl_PointSize = (2.0 + vAlpha * 2.0) * (30.0 / -mvPosition.z);
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  fragmentShader: `
    uniform vec3 u_color;
    varying float vAlpha;
    void main() {
      // Circular particle
      vec2 coord = gl_PointCoord - vec2(0.5);
      if(length(coord) > 0.5) discard;
      gl_FragColor = vec4(u_color, vAlpha * 0.6);
    }
  `
};

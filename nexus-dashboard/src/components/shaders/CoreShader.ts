import * as THREE from 'three';

export const CoreShaderMaterial = {
  uniforms: {
    u_time: { value: 0 },
    u_entropy: { value: 1.0 }, // eta (balance)
    u_drift: { value: 0.0 }, // KL divergence
    u_pulse: { value: 0.0 }, // 0 to 1 shockwave
    u_baseColor: { value: new THREE.Color('#ffffff') },
    u_isWireframe: { value: 0.0 }, // 0 = Solid Core, 1 = Lattice Glowing
    u_intensity: { value: 1.0 }
  },
  clone: function() {
    return {
      u_time: { value: 0 },
      u_entropy: { value: 1.0 },
      u_drift: { value: 0.0 },
      u_pulse: { value: 0.0 },
      u_baseColor: { value: new THREE.Color('#ffffff') },
      u_isWireframe: { value: 0.0 },
      u_intensity: { value: 1.0 }
    };
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
    uniform float u_isWireframe;
    uniform float u_intensity;
    
    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec3 vViewPosition;

    void main() {
      vec3 normal = normalize(vNormal);
      vec3 viewDir = normalize(vViewPosition);

      // FRESNEL (RIM SCATTERING) - Only strong on solid core
      float dotProduct = max(0.0, dot(normal, viewDir));
      float rim = 1.0 - dotProduct;
      float fresnel = pow(rim, 4.0);
      
      vec3 color = u_baseColor;
      
      // PROCEDURAL SCANLINES
      float scanline = sin(vPosition.y * 80.0 - u_time * 5.0) * 0.05;
      
      // DRIFT CONTAMINATION (Shift to Red/Amber during drift hazard)
      if (u_drift > 0.0) {
        float driftMix = min(u_drift * 5.0, 1.0);
        vec3 hazardColor = mix(vec3(1.0, 0.4, 0.0), vec3(1.0, 0.0, 0.1), driftMix);
        color = mix(color, hazardColor, driftMix * (0.5 + 0.5 * sin(u_time * 6.0)));
      }

      // PULSE OVERDRIVE (Supernova white flash)
      color = mix(color, vec3(1.0, 1.0, 1.0), u_pulse);
      
      // If wireframe: Multiply RGB intensity massively so Post-Processing Bloom catches it!
      // If solid core: Keep color solid, add fresnel rim lighting, adjust alpha for glass look.
      
      if (u_isWireframe > 0.5) {
          // ENERGY LATTICE 
          // Color * 3.0 * intensity breaks the 1.0 luminance limit -> generates extreme AAA Bloom
          gl_FragColor = vec4(color * 3.0 * u_intensity, 1.0);
      } else {
          // SOLID GLASS CORE
          float alpha = 0.5 + (fresnel * 0.5) + u_pulse + max(0.0, scanline);
          // Darken the core slightly, let the rim shine, apply intensity to Fresnel
          vec3 finalColor = color * (0.6 + fresnel * 0.7 * u_intensity);
          gl_FragColor = vec4(finalColor, min(alpha, 1.0));
      }
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

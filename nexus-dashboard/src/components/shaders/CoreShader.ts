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

    // Classic 3D noise could go here, but we'll use simple sin wave math for performance
    void main() {
      vUv = uv;
      vPosition = position;

      // Entropy determines how "stable" the geometry is. Low entropy = high distortion
      float instability = (1.0 - u_entropy) * 2.0; 
      
      // Drift adds higher frequency jitter
      float noise = sin(position.x * 10.0 + u_time * 5.0) * cos(position.y * 10.0 + u_time * 5.0);
      
      vec3 pos = position;
      
      // Apply ambient geometric distortion
      pos += normal * noise * instability * 0.1;
      pos += normal * sin(u_time * 10.0) * u_drift * 0.5;

      // Apply pulse shockwave (scales up vertices temporarily)
      pos += normal * u_pulse * 0.5;

      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    uniform float u_time;
    uniform float u_drift;
    uniform float u_pulse;
    uniform vec3 u_baseColor;
    
    varying vec3 vPosition;

    void main() {
      vec3 color = u_baseColor;

      // High drift shifts color towards red
      if (u_drift > 0.0) {
        float driftGlow = min(u_drift * 5.0, 1.0);
        color = mix(color, vec3(1.0, 0.2, 0.2), driftGlow * sin(u_time * 3.0));
      }

      // Pulse creates a bright white flash
      color = mix(color, vec3(1.0, 1.0, 1.0), u_pulse);

      // Wireframe intensity fade
      float alpha = 1.0;

      gl_FragColor = vec4(color, alpha);
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

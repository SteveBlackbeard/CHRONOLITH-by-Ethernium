import React, { useEffect, useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { useAnimations, useGLTF } from '@react-three/drei';
import * as THREE from 'three';
import { clone as cloneSkeleton } from 'three/examples/jsm/utils/SkeletonUtils.js';
import { GraphNode } from '@/lib/graphData';
import { getNodeAssetProfile, NodeAssetProfile, NodeAssetStage } from '@/lib/nodeAssets';

function tintMaterial(material: THREE.Material, accent: string, tintStrength: number, opacity: number) {
  const meshMaterial = material as THREE.Material & {
    color?: THREE.Color;
    emissive?: THREE.Color;
    emissiveIntensity?: number;
    opacity?: number;
    transparent?: boolean;
    metalness?: number;
    roughness?: number;
    side?: THREE.Side;
  };

  if (meshMaterial.color) {
    if (tintStrength > 0.001) {
      meshMaterial.color = meshMaterial.color.clone().lerp(new THREE.Color(accent), tintStrength);
    }
  }
  if (meshMaterial.emissive) {
    if (tintStrength > 0.001) {
      meshMaterial.emissive = new THREE.Color(accent).multiplyScalar(tintStrength * 0.3);
      meshMaterial.emissiveIntensity = 0.45;
    }
  }
  if (typeof meshMaterial.opacity === 'number') {
    meshMaterial.opacity = Math.min(meshMaterial.opacity, opacity);
  } else {
    meshMaterial.opacity = opacity;
  }
  meshMaterial.transparent = meshMaterial.opacity < 1;
  meshMaterial.side = THREE.DoubleSide;
  if (tintStrength > 0.001) {
    if (typeof meshMaterial.metalness === 'number') meshMaterial.metalness = Math.max(meshMaterial.metalness, 0.55);
    if (typeof meshMaterial.roughness === 'number') meshMaterial.roughness = Math.min(meshMaterial.roughness, 0.42);
  }
}

const TOP_DOWN_ASSET_ROTATION: [number, number, number] = [-Math.PI / 2, 0, 0];

function computeApproximateMassCenter(root: THREE.Object3D) {
  root.updateWorldMatrix(true, true);
  const weightedCenter = new THREE.Vector3();
  let totalWeight = 0;
  const vertex = new THREE.Vector3();
  const transformed = new THREE.Vector3();

  root.traverse((object) => {
    if (!(object as THREE.Mesh).isMesh) return;
    const mesh = object as THREE.Mesh;
    const geometry = mesh.geometry;
    const position = geometry?.getAttribute?.('position');
    if (!geometry || !position) return;
    const weight = Math.max(1, position.count || 0);
    const localCenter = new THREE.Vector3();

    for (let i = 0; i < position.count; i++) {
      vertex.fromBufferAttribute(position as THREE.BufferAttribute, i);
      localCenter.add(vertex);
    }

    localCenter.multiplyScalar(1 / weight);
    transformed.copy(localCenter).applyMatrix4(mesh.matrixWorld);
    weightedCenter.add(transformed.multiplyScalar(weight));
    totalWeight += weight;
  });

  if (totalWeight > 0) {
    return weightedCenter.multiplyScalar(1 / totalWeight);
  }

  const fallbackBounds = new THREE.Box3().setFromObject(root);
  return fallbackBounds.getCenter(new THREE.Vector3());
}

function AssetStageModel({
  stage,
  accent,
  tintStrength,
  scale,
  pulsing,
  selected,
}: {
  stage: NodeAssetStage;
  accent: string;
  tintStrength: number;
  scale: number;
  pulsing: boolean;
  selected: boolean;
}) {
  const groupRef = useRef<THREE.Group>(null!);
  const gltf = useGLTF(stage.src);
  const stageRotation = stage.rotation || [0, 0, 0];
  const resolvedRotation = useMemo<[number, number, number]>(
    () => [
      TOP_DOWN_ASSET_ROTATION[0] + stageRotation[0],
      TOP_DOWN_ASSET_ROTATION[1] + stageRotation[1],
      TOP_DOWN_ASSET_ROTATION[2] + stageRotation[2],
    ],
    [stageRotation],
  );
  const { scene, normalizationScale, normalizationOffset } = useMemo(() => {
    const clonedScene = cloneSkeleton(gltf.scene);
    const bounds = new THREE.Box3().setFromObject(clonedScene);
    const size = new THREE.Vector3();
    bounds.getSize(size);
    const center = stage.anchorMode === 'origin'
      ? new THREE.Vector3(0, 0, 0)
      : computeApproximateMassCenter(clonedScene);

    const planarFootprint = Math.max(size.x, size.z, 0.0001);
    const spatialFootprint = Math.max(size.x, size.y * 0.75, size.z, 0.0001);
    const canonicalFootprint = stage.normalizationMode === 'planar'
      ? planarFootprint
      : spatialFootprint;
    const nextNormalizationScale = 1 / canonicalFootprint;

    return {
      scene: clonedScene,
      normalizationScale: nextNormalizationScale,
      normalizationOffset: [-center.x, -center.y, -center.z] as [number, number, number],
    };
  }, [gltf.scene, stage.anchorMode, stage.normalizationMode]);
  const { actions, names } = useAnimations(gltf.animations, groupRef);

  useEffect(() => {
    scene.traverse((object) => {
      if (!(object as THREE.Mesh).isMesh) return;
      const mesh = object as THREE.Mesh;
      if (Array.isArray(mesh.material)) {
        mesh.material = mesh.material.map((entry) => {
          const next = entry.clone();
          tintMaterial(next, accent, tintStrength, stage.opacity ?? 1);
          return next;
        });
        return;
      }

      const next = mesh.material.clone();
      tintMaterial(next, accent, tintStrength, stage.opacity ?? 1);
      mesh.material = next;
    });
  }, [accent, scene, stage.opacity, tintStrength]);

  useEffect(() => {
    if (!stage.autoplay || !actions) return;
    const clipName = stage.animationClip === '__auto' ? names[0] : stage.animationClip;
    if (!clipName) return;
    const action = actions[clipName];
    action?.reset().fadeIn(0.25).play();
    return () => {
      action?.fadeOut(0.2);
    };
  }, [actions, names, stage.animationClip, stage.autoplay]);

  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.elapsedTime;
    const pulse = pulsing ? 1 + Math.sin(t * 8.4) * 0.02 : 1;
    const selectionLift = selected ? 1.03 : 1;
    groupRef.current.scale.setScalar((stage.scale || 1) * scale * pulse * selectionLift);

    if (stage.animatedMaterial) {
      groupRef.current.traverse((object) => {
        if (!(object as THREE.Mesh).isMesh) return;
        const mesh = object as THREE.Mesh;
        const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
        materials.forEach((material) => {
          const candidate = material as THREE.Material & { emissiveIntensity?: number };
          if (typeof candidate.emissiveIntensity === 'number') {
            candidate.emissiveIntensity = 0.18 + Math.abs(Math.sin(t * 1.6)) * 0.22 + (selected ? 0.1 : 0);
          }
        });
      });
    }
  });

  return (
    <group
      ref={groupRef}
      position={stage.offset || [0, 0, 0]}
      rotation={resolvedRotation}
    >
      <group position={normalizationOffset} scale={normalizationScale}>
        <primitive object={scene} />
      </group>
    </group>
  );
}

export default function NodeAssetRig({
  node,
  accent,
  scale,
  pulsing,
  selected,
  profile,
}: {
  node: GraphNode;
  accent: string;
  scale: number;
  pulsing: boolean;
  selected: boolean;
  profile?: NodeAssetProfile;
}) {
  const resolvedProfile = profile || getNodeAssetProfile(node);

  return (
    <group>
      {resolvedProfile.appearance.enabled && (
        <AssetStageModel
          stage={resolvedProfile.appearance}
          accent={accent}
          tintStrength={resolvedProfile.tintStrength || 0.16}
          scale={scale}
          pulsing={pulsing}
          selected={selected}
        />
      )}
    </group>
  );
}

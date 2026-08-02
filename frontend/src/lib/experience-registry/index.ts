import React from 'react';

// Scene Registry
export interface SceneManifest {
  id: string;
  component: React.ComponentType<any>;
  defaultQuality: 'ultra' | 'high' | 'medium' | 'low';
}
const SCENES = new Map<string, SceneManifest>();
export const registerScene = (manifest: SceneManifest) => SCENES.set(manifest.id, manifest);
export const getScene = (id: string) => SCENES.get(id);

// Background Registry
export interface BackgroundManifest {
  id: string;
  component: React.ComponentType<any>;
}
const BACKGROUNDS = new Map<string, BackgroundManifest>();
export const registerBackground = (manifest: BackgroundManifest) => BACKGROUNDS.set(manifest.id, manifest);
export const getBackground = (id: string) => BACKGROUNDS.get(id);

// Animation Registry (Framer Motion Variants)
const ANIMATIONS = new Map<string, any>();
export const registerAnimation = (id: string, variants: any) => ANIMATIONS.set(id, variants);
export const getAnimation = (id: string) => ANIMATIONS.get(id);

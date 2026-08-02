export interface Artifact {
  id: string;
  name: string;
  version: number;
  category: string;
  mimeType: string;
  sizeBytes: number;
  createdAt: string;
  updatedAt: string;
  author: string;
  tags: string[];
  content: string; // The raw content
}

export type DeviceProfile = 'desktop' | 'laptop' | 'tablet' | 'mobile' | 'responsive';

export interface PreviewSession {
  artifactId: string | null;
  version: number | null;
  deviceProfile: DeviceProfile;
  zoom: number;
  fullscreen: boolean;
  compareMode: boolean;
  rendererMode: 'preview' | 'source' | 'split';
  compareArtifactId: string | null;
}

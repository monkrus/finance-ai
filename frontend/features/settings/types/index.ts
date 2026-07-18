export interface UserProfile {
  id: string;
  name: string;
  email: string;
  username: string;
  phone?: string;
  bio?: string;
  country: string;
  timezone: string;
  language: string;
  currency: string;
  occupation?: string;
  avatarUrl?: string;
}

export interface SecurityStatus {
  twoFactorEnabled: boolean;
  trustedDevicesCount: number;
  activeSessions: Session[];
  securityScore: number;
}

export interface Session {
  id: string;
  device: string;
  browser: string;
  location: string;
  ip: string;
  lastActive: string;
  isCurrent: boolean;
}

export interface Integration {
  id: string;
  provider: string;
  type: 'bank' | 'broker' | 'exchange' | 'csv';
  status: 'connected' | 'disconnected' | 'error';
  lastSync?: string;
  health: number;
}

export interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  created: string;
  expires?: string;
  lastUsed?: string;
  permissions: string[];
}

export interface AuditLog {
  id: string;
  action: string;
  actor: string;
  timestamp: string;
  ip: string;
  details: string;
}

export interface SystemMetrics {
  version: string;
  redis: 'ONLINE' | 'OFFLINE' | 'DEGRADED';
  database: 'ONLINE' | 'OFFLINE' | 'DEGRADED';
  queueDepth: number;
  activeWorkers: number;
  environment: string;
}

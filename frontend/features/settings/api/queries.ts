import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { UserProfile, SecurityStatus, Integration, ApiKey, AuditLog, SystemMetrics } from '../types';

export function useUserProfile() {
  return useQuery({
    queryKey: ['settings', 'profile'],
    queryFn: async () => {
      const res = await apiClient.get<UserProfile>('/api/v1/users/me');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useSecurityStatus() {
  return useQuery({
    queryKey: ['settings', 'security'],
    queryFn: async () => {
      const res = await apiClient.get<SecurityStatus>('/api/v1/auth/security');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useIntegrations() {
  return useQuery({
    queryKey: ['settings', 'integrations'],
    queryFn: async () => {
      const res = await apiClient.get<Integration[]>('/api/v1/integrations');
      return res.data;
    },
    staleTime: 60 * 1000,
  });
}

export function useApiKeys() {
  return useQuery({
    queryKey: ['settings', 'apiKeys'],
    queryFn: async () => {
      const res = await apiClient.get<ApiKey[]>('/api/v1/integrations/keys');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useAuditLogs() {
  return useQuery({
    queryKey: ['settings', 'audit'],
    queryFn: async () => {
      const res = await apiClient.get<AuditLog[]>('/api/v1/integrations/audit');
      return res.data;
    },
    staleTime: 60 * 1000,
  });
}

export function useSystemMetrics() {
  return useQuery({
    queryKey: ['settings', 'admin', 'metrics'],
    queryFn: async () => {
      const res = await apiClient.get<SystemMetrics>('/api/v1/admin/metrics');
      return res.data;
    },
    refetchInterval: 30000,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<UserProfile>) => {
      await apiClient.put('/api/v1/users/me', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'profile'] });
    }
  });
}

import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { Notification, AutomationRule, PreferenceSetting, ActivityEvent } from '../types';

export function useNotifications() {
  return useInfiniteQuery({
    queryKey: ['notifications', 'feed'],
    queryFn: async ({ pageParam = 1 }) => {
      const res = await apiClient.get<Notification[] | { notifications: Notification[]; nextCursor: number | null }>(
        `/api/v1/notifications?page=${pageParam}`
      );
      // The API returns a plain array of notifications (it does not paginate).
      // Normalize to the paged shape this feed consumes so the list is always
      // a real array; a non-array here previously produced [undefined] entries.
      const payload = res.data;
      if (Array.isArray(payload)) {
        return { notifications: payload, nextCursor: null };
      }
      return {
        notifications: payload?.notifications ?? [],
        nextCursor: payload?.nextCursor ?? null,
      };
    },
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: 1,
    staleTime: 60 * 1000,
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: ['notifications', 'unreadCount'],
    queryFn: async () => {
      // Backend exposes the unread notifications themselves, not a count.
      const res = await apiClient.get<unknown[]>('/api/v1/notifications/unread');
      return Array.isArray(res.data) ? res.data.length : 0;
    },
    refetchInterval: 30000,
  });
}

export function useAutomations() {
  return useQuery({
    queryKey: ['notifications', 'automations'],
    queryFn: async () => {
      // Automation rules are exposed as /notifications/rules.
      const res = await apiClient.get<AutomationRule[]>('/api/v1/notifications/rules');
      return res.data ?? [];
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function usePreferences() {
  return useQuery({
    queryKey: ['notifications', 'preferences'],
    queryFn: async () => {
      const res = await apiClient.get<PreferenceSetting[]>('/api/v1/notifications/preferences');
      return res.data;
    },
    staleTime: 60 * 60 * 1000,
  });
}

export function useActivityTimeline() {
  return useQuery({
    queryKey: ['notifications', 'timeline'],
    queryFn: async () => {
      // The notification history endpoint backs the activity timeline.
      const res = await apiClient.get<ActivityEvent[]>('/api/v1/notifications/history');
      return res.data ?? [];
    },
    staleTime: 2 * 60 * 1000,
  });
}

// Mutations
export function useMarkAsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      // Backend route is /notifications/read/{id}.
      await apiClient.post(`/api/v1/notifications/read/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    }
  });
}

export function useArchiveNotification() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      // Backend route is /notifications/archive/{id}.
      await apiClient.post(`/api/v1/notifications/archive/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    }
  });
}

export function useToggleAutomation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, status }: { id: string, status: 'active' | 'paused' }) => {
      await apiClient.put(`/api/v1/notifications/automations/${id}`, { status });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications', 'automations'] });
    }
  });
}

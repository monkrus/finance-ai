import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { ChatSession, SuggestedPrompt, ActiveContext, ChatMessage } from '../types';

// Send a chat message. This is the one AI endpoint the backend implements:
//   POST /api/v1/ai/chat  { session_id, message, stream }  ->  { response }
// stream:false is used because the frontend does not consume the SSE stream.
export function useSendChatMessage() {
  return useMutation({
    mutationFn: async ({ sessionId, message }: { sessionId: string; message: string }) => {
      const res = await apiClient.post<{ response: string }>('/api/v1/ai/chat', {
        session_id: sessionId,
        message,
        stream: false,
      });
      return res.data.response;
    },
  });
}

// History. The backend exposes no chat-history endpoint, so history is empty
// on the client rather than issuing a request that would 404.
export function useChatHistory() {
  return useQuery({
    queryKey: ['ai', 'history'],
    queryFn: async (): Promise<ChatSession[]> => [],
    staleTime: 60 * 1000,
  });
}

// Single Session. The backend keeps conversation memory server-side (keyed by
// session id) but exposes no endpoint to load prior messages, so a freshly
// opened session starts empty on the client. Follow-ups still carry context
// server-side via the session id.
export function useChatSession(_id: string) {
  return useQuery({
    queryKey: ['ai', 'session', _id],
    queryFn: async (): Promise<ChatMessage[]> => [],
    staleTime: 5 * 60 * 1000,
  });
}

// Suggested Prompts
export function useSuggestedPrompts() {
  return useQuery({
    queryKey: ['ai', 'prompts'],
    queryFn: async () => {
      const res = await apiClient.get<SuggestedPrompt[]>('/api/v1/ai/prompts');
      return res.data;
    },
    staleTime: 60 * 60 * 1000,
  });
}

// Context
export function useActiveContext() {
  return useQuery({
    queryKey: ['ai', 'context'],
    queryFn: async () => {
      const res = await apiClient.get<ActiveContext>('/api/v1/ai/context');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

// Mutations
export function useDeleteSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/ai/session/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai', 'history'] });
    }
  });
}

export function useRenameSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, title }: { id: string, title: string }) => {
      await apiClient.put(`/api/v1/ai/session/${id}`, { title });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai', 'history'] });
    }
  });
}

export function useUploadFile() {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post<{ id: string, url: string }>('/api/v1/ai/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return res.data;
    }
  });
}

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import { ChatContainer } from '@/features/ai/chat/ChatContainer';
import { apiClient } from '@/services/api';
import { useSendChatMessage } from '@/features/ai/api/queries';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// --- Mock the AI query hooks so ChatContainer's behavior is tested in isolation.
const mockMutateAsync = jest.fn();
jest.mock('@/features/ai/api/queries', () => ({
  useChatSession: jest.fn(),
  useSendChatMessage: jest.fn(),
}));

// --- Mock heavy leaf modules (ESM markdown/animation) to keep the test focused.
jest.mock('@/features/ai/chat/MarkdownRenderer', () => ({
  MarkdownRenderer: ({ content }: { content: string }) => <div>{content}</div>,
}));
jest.mock('@/features/ai/chat/ToolExecutionCard', () => ({ ToolExecutionCard: () => null }));
jest.mock('@/features/ai/chat/ChartCard', () => ({ ChartCard: () => null }));
jest.mock('@/features/ai/chat/CitationCard', () => ({ CitationCard: () => null }));
jest.mock('framer-motion', () => ({
  __esModule: true,
  motion: new Proxy(
    {},
    { get: () => ({ children }: any) => <div>{children}</div> }
  ),
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

const { useChatSession } = jest.requireMock('@/features/ai/api/queries');

function typeAndSend(text: string) {
  const textarea = screen.getByPlaceholderText('Ask FinPilot...');
  fireEvent.change(textarea, { target: { value: text } });
  fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
}

describe('AI Copilot — ChatContainer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useChatSession as jest.Mock).mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      refetch: jest.fn(),
    });
    (useSendChatMessage as jest.Mock).mockReturnValue({ mutateAsync: mockMutateAsync });
  });

  it('successful conversation: sends to the backend and renders the response', async () => {
    mockMutateAsync.mockResolvedValue('Diversification spreads risk across assets.');
    render(<ChatContainer sessionId="s1" />);

    typeAndSend('What is diversification?');

    // User message echoed
    expect(screen.getByText('What is diversification?')).toBeInTheDocument();
    // Correct payload sent to the backend
    expect(mockMutateAsync).toHaveBeenCalledWith({ sessionId: 's1', message: 'What is diversification?' });
    // Assistant response rendered
    await waitFor(() =>
      expect(screen.getByText('Diversification spreads risk across assets.')).toBeInTheDocument()
    );
  });

  it('backend error: shows a friendly error message', async () => {
    mockMutateAsync.mockRejectedValue(new Error('500'));
    render(<ChatContainer sessionId="s1" />);

    typeAndSend('Analyze my portfolio');

    await waitFor(() =>
      expect(
        screen.getByText('Something went wrong reaching FinPilot AI. Please try again.')
      ).toBeInTheDocument()
    );
  });

  it('AI provider unavailable: maps the backend fallback to a friendly message', async () => {
    // Backend returns HTTP 200 with this fallback text when no provider is configured.
    mockMutateAsync.mockResolvedValue(
      'An error occurred while fetching the required data: . Please inform the user gracefully.'
    );
    render(<ChatContainer sessionId="s1" />);

    typeAndSend('Hello');

    await waitFor(() =>
      expect(
        screen.getByText('FinPilot AI is temporarily unavailable. Please try again in a moment.')
      ).toBeInTheDocument()
    );
    // The raw internal fallback text is never shown to the user.
    expect(screen.queryByText(/inform the user gracefully/i)).not.toBeInTheDocument();
  });

  it('authentication failure: surfaces a friendly error (no crash)', async () => {
    mockMutateAsync.mockRejectedValue({ response: { status: 401 } });
    render(<ChatContainer sessionId="s1" />);

    typeAndSend('Secure request');

    await waitFor(() =>
      expect(
        screen.getByText('Something went wrong reaching FinPilot AI. Please try again.')
      ).toBeInTheDocument()
    );
  });

  it('empty prompt: does not call the backend', () => {
    render(<ChatContainer sessionId="s1" />);
    typeAndSend('   ');
    expect(mockMutateAsync).not.toHaveBeenCalled();
  });

  it('multiple sequential prompts: each reaches the backend and renders', async () => {
    mockMutateAsync.mockResolvedValueOnce('First answer').mockResolvedValueOnce('Second answer');
    render(<ChatContainer sessionId="s1" />);

    typeAndSend('First question');
    await waitFor(() => expect(screen.getByText('First answer')).toBeInTheDocument());

    typeAndSend('Second question');
    await waitFor(() => expect(screen.getByText('Second answer')).toBeInTheDocument());

    expect(mockMutateAsync).toHaveBeenCalledTimes(2);
    expect(screen.getByText('First question')).toBeInTheDocument();
    expect(screen.getByText('Second question')).toBeInTheDocument();
  });

  it('conversation rendering: initial session messages are displayed', () => {
    (useChatSession as jest.Mock).mockReturnValue({
      data: [
        { id: 'm1', role: 'user', content: 'Prior question', timestamp: '', status: 'complete' },
        { id: 'm2', role: 'assistant', content: 'Prior answer', timestamp: '', status: 'complete' },
      ],
      isLoading: false,
      isError: false,
      refetch: jest.fn(),
    });
    render(<ChatContainer sessionId="s1" />);
    expect(screen.getByText('Prior question')).toBeInTheDocument();
    expect(screen.getByText('Prior answer')).toBeInTheDocument();
  });
});

describe('AI Copilot — useSendChatMessage contract', () => {
  it('POSTs the correct endpoint and payload, returning the response', async () => {
    const actual = jest.requireActual('@/features/ai/api/queries');
    const mock = new MockAdapter(apiClient);
    let capturedBody: any;
    mock.onPost('/api/v1/ai/chat').reply((config) => {
      capturedBody = JSON.parse(config.data);
      return [200, { response: 'ok-from-backend' }];
    });

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { renderHook } = await import('@testing-library/react');
    const { result } = renderHook(() => actual.useSendChatMessage(), { wrapper });

    const response = await result.current.mutateAsync({ sessionId: 'sess', message: 'hi' });

    expect(capturedBody).toEqual({ session_id: 'sess', message: 'hi', stream: false });
    expect(response).toBe('ok-from-backend');
    mock.restore();
  });
});

"use client";

import React, { useState, useRef, useEffect } from 'react';
import { useChatSession, useSendChatMessage } from '../api/queries';
import { ChatInput } from './ChatInput';
import { MarkdownRenderer } from './MarkdownRenderer';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Sparkles, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ChatMessage } from '../types';
import { ToolExecutionCard } from './ToolExecutionCard';
import { ChartCard } from './ChartCard';
import { CitationCard } from './CitationCard';

// Friendly, user-facing copy for the failure paths. The backend degrades
// gracefully (HTTP 200 with a fallback string) when the AI provider is not
// configured, so that case is detected from the response text.
const UNAVAILABLE_MESSAGE =
  'FinPilot AI is temporarily unavailable. Please try again in a moment.';
const ERROR_MESSAGE =
  'Something went wrong reaching FinPilot AI. Please try again.';

function isBackendUnavailableResponse(response: string): boolean {
  return (
    response.includes('Please inform the user gracefully') ||
    response.includes('An error occurred while fetching the required data')
  );
}

export function ChatContainer({ sessionId }: { sessionId: string }) {
  const { data: initialMessages, isLoading, isError, refetch } = useChatSession(sessionId);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const sendMessage = useSendChatMessage();
  const initialQuerySent = useRef(false);

  useEffect(() => {
    // Only seed from loaded history; never overwrite the live conversation with
    // an empty result (the backend exposes no history endpoint, so this stays a
    // no-op today and simply preserves in-session messages).
    if (initialMessages && initialMessages.length > 0) {
      setMessages(initialMessages);
    }
  }, [initialMessages]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  const handleSend = async (content: string) => {
    const trimmed = content.trim();
    if (!trimmed) return; // never send an empty prompt (backend rejects with 400)

    const userMsg: ChatMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      content: trimmed,
      timestamp: new Date().toISOString(),
      status: 'complete',
    };
    setMessages(prev => [...prev, userMsg]);
    setIsStreaming(true);

    let assistantContent: string;
    let assistantStatus: ChatMessage['status'] = 'complete';
    try {
      const response = await sendMessage.mutateAsync({ sessionId, message: trimmed });
      if (isBackendUnavailableResponse(response)) {
        assistantContent = UNAVAILABLE_MESSAGE;
        assistantStatus = 'error';
      } else {
        assistantContent = response;
      }
    } catch {
      // Network / 5xx / auth failure. (401s are transparently retried by the
      // API client's refresh interceptor before this catch is reached.)
      assistantContent = ERROR_MESSAGE;
      assistantStatus = 'error';
    }

    const assistantMsg: ChatMessage = {
      id: `${Date.now()}-assistant`,
      role: 'assistant',
      content: assistantContent,
      timestamp: new Date().toISOString(),
      status: assistantStatus,
    };
    setMessages(prev => [...prev, assistantMsg]);
    setIsStreaming(false);
  };

  // A first message can be carried in via ?q= (from the landing input or a
  // suggested prompt). Send it exactly once, then strip it from the URL so a
  // refresh does not re-send it.
  useEffect(() => {
    if (typeof window === 'undefined' || initialQuerySent.current) return;
    const initialQuery = new URLSearchParams(window.location.search).get('q');
    if (initialQuery) {
      initialQuerySent.current = true;
      handleSend(initialQuery);
      window.history.replaceState({}, '', `/ai/chat/${sessionId}`);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isError) return <div className="flex-1 flex items-center justify-center p-8"><WidgetError title="Session Error" message="Failed to load chat." onRetry={refetch} /></div>;

  return (
    <main className="flex-1 flex flex-col relative h-full">
      {/* Ambient backgrounds */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none" />
      
      {/* Header */}
      <div className="h-14 border-b border-white/5 flex items-center px-6 shrink-0 relative z-10 bg-background/50 backdrop-blur-md">
        <div className="text-sm font-medium">FinPilot AI</div>
      </div>

      {/* Message Feed */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6 relative z-10 scroll-smooth">
        {isLoading ? (
          <div className="space-y-6 max-w-3xl mx-auto w-full">
            <Skeleton className="h-20 w-3/4 rounded-2xl" />
            <Skeleton className="h-32 w-full rounded-2xl ml-auto" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <Sparkles className="h-12 w-12 mb-4 opacity-50" />
            <p>Start a conversation...</p>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto w-full space-y-8">
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
            </AnimatePresence>
            {isStreaming && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }} 
                animate={{ opacity: 1, y: 0 }} 
                className="flex items-center gap-2 text-muted-foreground text-sm pl-12"
              >
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                FinPilot is thinking...
              </motion.div>
            )}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 md:p-6 pt-0 relative z-20">
        <div className="max-w-3xl mx-auto w-full">
          <ChatInput onSend={handleSend} isStreaming={isStreaming} />
          <div className="mt-2 text-center text-[10px] text-muted-foreground opacity-60">
            FinPilot AI can make mistakes. Verify important financial data.
          </div>
        </div>
      </div>
    </main>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("flex gap-4", isUser ? "flex-row-reverse" : "")}
    >
      <div className={cn(
        "shrink-0 h-8 w-8 rounded-full flex items-center justify-center border border-white/10 shadow-sm",
        isUser ? "bg-muted" : "bg-indigo-600"
      )}>
        {isUser ? <User className="h-4 w-4" /> : <Sparkles className="h-4 w-4 text-white" />}
      </div>
      
      <div className={cn(
        "flex flex-col gap-2 max-w-[85%]",
        isUser ? "items-end" : "items-start"
      )}>
        <div className={cn(
          "px-5 py-3.5 rounded-2xl shadow-sm border border-white/5",
          isUser 
            ? "bg-muted text-foreground rounded-tr-none" 
            : "bg-card/60 backdrop-blur-md rounded-tl-none prose prose-invert prose-p:leading-relaxed prose-pre:bg-black/50 max-w-none"
        )}>
          {isUser ? (
            <div className="whitespace-pre-wrap">{message.content}</div>
          ) : (
            <MarkdownRenderer content={message.content} />
          )}
        </div>

        {!isUser && message.toolCalls && message.toolCalls.map(tool => (
          <ToolExecutionCard key={tool.id} tool={tool} />
        ))}
        
        {!isUser && message.inlineData?.chart && (
          <ChartCard intent={message.inlineData.chart} />
        )}
        
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {message.citations.map(c => <CitationCard key={c.id} citation={c} />)}
          </div>
        )}
      </div>
    </motion.div>
  );
}

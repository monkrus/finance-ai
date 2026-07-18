'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ChatInput } from './ChatInput';

/**
 * The AI landing page (a server component) shows the chat input before a
 * session exists. Sending here starts a new chat session and carries the first
 * message into it via ?q=, where ChatContainer sends it to the backend.
 */
export function LandingChatInput() {
  const router = useRouter();

  const handleSend = (message: string) => {
    const trimmed = message.trim();
    if (!trimmed) return;
    const sessionId = Math.random().toString(36).substring(2, 10);
    router.push(`/ai/chat/${sessionId}?q=${encodeURIComponent(trimmed)}`);
  };

  return <ChatInput onSend={handleSend} />;
}

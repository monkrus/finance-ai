import { Metadata } from 'next';
import { HistorySidebar } from '@/features/ai/history/HistorySidebar';
import { ChatContainer } from '@/features/ai/chat/ChatContainer';

export const metadata: Metadata = {
  title: 'AI Chat | FinPilot AI',
};

export default async function ChatPage({ params }: { params: Promise<{ id: string }> }) {
  const p = await params;

  return (
    <div className="flex h-[calc(100vh-6rem)] overflow-hidden rounded-2xl border border-white/5 bg-background/50 backdrop-blur-3xl shadow-2xl relative">
      <HistorySidebar />
      <ChatContainer sessionId={p.id} />
    </div>
  );
}

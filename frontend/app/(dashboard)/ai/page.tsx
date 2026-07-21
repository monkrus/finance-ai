import React from 'react';
import { Metadata } from 'next';
import { HistorySidebar } from '@/features/ai/history/HistorySidebar';
import { PromptCard } from '@/features/ai/components/PromptCard';
import { LandingChatInput } from '@/features/ai/chat/LandingChatInput';
import { Sparkles, Activity, Globe, Wallet } from 'lucide-react';

export const metadata: Metadata = {
  title: 'AI Copilot | FinPilot AI',
};

// NextJS Server Component wrapper for the landing page
export default function AICopilotLanding() {
  return (
    <div className="flex h-[calc(100vh-6rem)] overflow-hidden rounded-2xl border border-white/5 bg-background/50 backdrop-blur-3xl shadow-2xl">
      <HistorySidebar />
      
      <main className="flex-1 flex flex-col relative h-full">
        {/* Ambient background */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-fuchsia-500/10 rounded-full blur-[120px] pointer-events-none translate-y-1/2 -translate-x-1/2" />

        <div className="flex-1 flex flex-col items-center justify-center p-8 overflow-y-auto custom-scrollbar relative z-10">
          <div className="w-full max-w-3xl space-y-12">
            
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center p-3 bg-indigo-500/10 rounded-2xl mb-4 border border-white/5">
                <Sparkles className="h-8 w-8 text-indigo-400" />
              </div>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-white to-white/60">
                Good morning. How can I help?
              </h1>
              <p className="text-muted-foreground text-lg">
                I can analyze your portfolio, summarize market news, or assist with financial planning.
              </p>
            </div>

            <SuggestedPromptsGrid />
          </div>
        </div>

        <div className="p-4 md:p-8 pt-0 relative z-20">
          <div className="max-w-3xl mx-auto w-full">
            <LandingChatInput />
            <div className="mt-4 flex justify-center gap-6 text-xs text-muted-foreground">
              <ContextBadge icon={<Activity />} label="Portfolio Active" />
              <ContextBadge icon={<Globe />} label="News Active" />
              <ContextBadge icon={<Wallet />} label="Wealth Active" />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// Separate client component for data fetching

function SuggestedPromptsGrid() {
  // In a real app we'd fetch this from useSuggestedPrompts, but for landing we can use static defaults if loading
  const prompts = [
    { title: "Portfolio Analysis", description: "How is my tech exposure holding up?", category: "Portfolio" },
    { title: "Market Research", description: "Summarize the latest fed rate decisions.", category: "Market" },
    { title: "Wealth Planning", description: "Am I on track for my FIRE goal?", category: "Wealth" },
    { title: "Stock Comparison", description: "Compare AAPL and MSFT financials.", category: "General" }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {prompts.map((p, i) => (
        <PromptCard key={i} title={p.title} description={p.description} category={p.category} />
      ))}
    </div>
  );
}

function ContextBadge({ icon, label }: any) {
  return (
    <div className="flex items-center gap-1.5 opacity-60">
      <div className="text-emerald-500">
        {React.cloneElement(icon, { className: 'h-3 w-3' })}
      </div>
      {label}
    </div>
  );
}

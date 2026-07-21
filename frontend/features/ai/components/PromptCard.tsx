'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowRight, Briefcase, Globe, PieChart, Activity } from 'lucide-react';
import { useRouter } from 'next/navigation';

export function PromptCard({ title, description, category }: { title: string, description: string, category: string }) {
  const router = useRouter();

  const handleSelect = () => {
    // Start a new chat and carry the prompt in as the first message (?q=),
    // which ChatContainer sends to the backend on mount.
    const newChatId = Math.random().toString(36).substring(2, 10);
    router.push(`/ai/chat/${newChatId}?q=${encodeURIComponent(description)}`);
  };

  const getIcon = () => {
    switch (category) {
      case 'Portfolio': return <PieChart className="h-5 w-5 text-indigo-400" />;
      case 'Market': return <Globe className="h-5 w-5 text-emerald-400" />;
      case 'Wealth': return <Briefcase className="h-5 w-5 text-amber-400" />;
      default: return <Activity className="h-5 w-5 text-fuchsia-400" />;
    }
  };

  return (
    <Card 
      onClick={handleSelect}
      className="bg-card/40 backdrop-blur-md border-white/5 hover:bg-card/60 transition-all cursor-pointer group hover:border-indigo-500/30"
    >
      <CardContent className="p-4 flex gap-4 items-start">
        <div className="shrink-0 p-2 bg-background rounded-lg border border-white/5 group-hover:scale-110 transition-transform">
          {getIcon()}
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-center mb-1">
            <h4 className="font-semibold text-sm group-hover:text-indigo-400 transition-colors">{title}</h4>
            <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
          </div>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
      </CardContent>
    </Card>
  );
}

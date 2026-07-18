"use client";

import React from 'react';
import { useChatHistory } from '../api/queries';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, MessageSquare, MoreVertical, Pin, Trash, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

export function HistorySidebar() {
  const { data, isLoading } = useChatHistory();
  const params = useParams();
  const router = useRouter();
  const currentId = params?.id as string;

  return (
    <div className="w-72 border-r border-white/5 bg-card/40 flex flex-col h-full shrink-0">
      <div className="p-4 border-b border-white/5 space-y-4">
        <Button 
          className="w-full justify-start bg-indigo-600 hover:bg-indigo-700"
          onClick={() => router.push('/ai')}
        >
          <Plus className="h-4 w-4 mr-2" /> New Chat
        </Button>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search history..." 
            className="pl-9 h-8 bg-background/50 border-white/10 text-xs"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-6">
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-8 w-full rounded" />
            <Skeleton className="h-8 w-full rounded" />
            <Skeleton className="h-8 w-full rounded" />
          </div>
        ) : (
          <>
            {/* Pinned */}
            {data?.filter(s => s.pinned).length ? (
              <div className="space-y-1">
                <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground px-2 mb-2">Pinned</div>
                {data.filter(s => s.pinned).map(session => (
                  <SessionLink key={session.id} session={session} isActive={currentId === session.id} />
                ))}
              </div>
            ) : null}

            {/* Recent */}
            <div className="space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground px-2 mb-2">Recent</div>
              {data?.filter(s => !s.pinned).slice(0,10).map(session => (
                <SessionLink key={session.id} session={session} isActive={currentId === session.id} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function SessionLink({ session, isActive }: { session: any, isActive: boolean }) {
  return (
    <Link 
      href={`/ai/chat/${session.id}`}
      className={cn(
        "group flex items-center justify-between px-2 py-2 rounded-md text-sm transition-colors",
        isActive ? "bg-indigo-500/20 text-indigo-100" : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
      )}
    >
      <div className="flex items-center gap-2 overflow-hidden">
        <MessageSquare className={cn("h-4 w-4 shrink-0", isActive ? "text-indigo-400" : "opacity-50")} />
        <span className="truncate">{session.title}</span>
      </div>
      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" size="icon" className="h-6 w-6 hover:bg-white/10">
          <MoreVertical className="h-3 w-3" />
        </Button>
      </div>
    </Link>
  );
}

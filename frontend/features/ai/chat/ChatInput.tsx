"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Paperclip, Mic, Send } from 'lucide-react';
import TextareaAutosize from 'react-textarea-autosize';

interface ChatInputProps {
  onSend?: (msg: string) => void;
  isStreaming?: boolean;
}

export function ChatInput({ onSend, isStreaming }: ChatInputProps) {
  const [value, setValue] = useState('');

  const handleSend = () => {
    if (!value.trim() || isStreaming) return;
    onSend?.(value);
    setValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative bg-card/60 backdrop-blur-2xl border border-white/10 rounded-3xl p-2 shadow-2xl overflow-hidden focus-within:border-indigo-500/50 transition-colors">
      <div className="flex items-end gap-2">
        <Button variant="ghost" size="icon" className="shrink-0 rounded-full h-10 w-10 text-muted-foreground hover:text-foreground hover:bg-white/10">
          <Paperclip className="h-5 w-5" />
        </Button>
        
        <TextareaAutosize
          maxRows={6}
          minRows={1}
          placeholder="Ask FinPilot..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 bg-transparent border-0 resize-none focus:ring-0 text-base py-2.5 outline-none custom-scrollbar"
        />

        {value.trim().length === 0 ? (
          <Button variant="ghost" size="icon" className="shrink-0 rounded-full h-10 w-10 text-muted-foreground hover:text-foreground hover:bg-white/10">
            <Mic className="h-5 w-5" />
          </Button>
        ) : (
          <Button 
            size="icon" 
            className="shrink-0 rounded-full h-10 w-10 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/20"
            onClick={handleSend}
            disabled={isStreaming}
          >
            <Send className="h-4 w-4 ml-0.5" />
          </Button>
        )}
      </div>
    </div>
  );
}

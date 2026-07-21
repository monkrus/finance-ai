import React from 'react';
import { ToolCall } from '../types';
import { Loader2, CheckCircle2, AlertCircle, Wrench } from 'lucide-react';
import { motion } from 'framer-motion';

export function ToolExecutionCard({ tool }: { tool: ToolCall }) {
  return (
    <motion.div 
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      className="bg-background/40 border border-white/5 rounded-lg px-3 py-2 flex items-center gap-3 w-fit mb-2"
    >
      <div className="shrink-0">
        {tool.status === 'running' && <Loader2 className="h-4 w-4 text-indigo-400 animate-spin" />}
        {tool.status === 'completed' && <CheckCircle2 className="h-4 w-4 text-emerald-500" />}
        {tool.status === 'failed' && <AlertCircle className="h-4 w-4 text-destructive" />}
      </div>
      <div className="flex flex-col">
        <span className="text-xs font-medium flex items-center gap-1.5">
          <Wrench className="h-3 w-3 text-muted-foreground" />
          {tool.name}
        </span>
        {tool.durationMs && (
          <span className="text-[10px] text-muted-foreground">{tool.durationMs}ms</span>
        )}
      </div>
    </motion.div>
  );
}

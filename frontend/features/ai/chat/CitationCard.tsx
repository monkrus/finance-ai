import React from 'react';
import { Citation } from '../types';
import { ExternalLink, FileText } from 'lucide-react';
import { motion } from 'framer-motion';

export function CitationCard({ citation }: { citation: Citation }) {
  const Comp = citation.url ? 'a' : 'div';
  const props = citation.url ? { href: citation.url, target: '_blank', rel: 'noopener noreferrer' } : {};

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <Comp 
        {...props}
        className="inline-flex items-center gap-2 bg-muted/50 hover:bg-muted border border-white/5 rounded-full px-3 py-1.5 text-xs transition-colors cursor-pointer group"
      >
        <FileText className="h-3 w-3 text-indigo-400 shrink-0" />
        <span className="truncate max-w-[150px] font-medium group-hover:text-indigo-400 transition-colors">
          {citation.title}
        </span>
        <span className="text-[10px] text-muted-foreground border-l border-white/10 pl-2">
          {citation.source}
        </span>
        {citation.url && <ExternalLink className="h-3 w-3 text-muted-foreground opacity-50 group-hover:opacity-100" />}
      </Comp>
    </motion.div>
  );
}

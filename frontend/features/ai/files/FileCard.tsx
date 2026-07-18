import React from 'react';
import { FileText, Download, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';

export function FileCard({ file, onRemove }: { file: File, onRemove?: () => void }) {
  const size = (file.size / 1024 / 1024).toFixed(2);
  
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-card/40 border border-white/10 rounded-lg p-3 flex items-center gap-3 w-64 shadow-sm"
    >
      <div className="h-10 w-10 shrink-0 bg-indigo-500/10 rounded-lg flex items-center justify-center border border-white/5">
        <FileText className="h-5 w-5 text-indigo-400" />
      </div>
      <div className="flex-1 overflow-hidden">
        <p className="text-sm font-medium truncate">{file.name}</p>
        <p className="text-xs text-muted-foreground">{size} MB</p>
      </div>
      {onRemove ? (
        <Button variant="ghost" size="icon" onClick={onRemove} className="h-6 w-6 rounded-full shrink-0 hover:bg-white/10">
          <X className="h-3 w-3" />
        </Button>
      ) : (
        <Button variant="ghost" size="icon" className="h-6 w-6 rounded-full shrink-0 hover:bg-white/10">
          <Download className="h-3 w-3" />
        </Button>
      )}
    </motion.div>
  );
}

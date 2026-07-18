"use client";

import React from 'react';
import { motion } from 'framer-motion';

export function MarketHero() {
  return (
    <div className="relative w-full rounded-2xl overflow-hidden mb-8 h-48 md:h-64 flex items-center bg-gradient-to-br from-indigo-900/40 via-blue-900/20 to-background border border-white/10 shadow-lg">
      <motion.div 
        animate={{ 
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        className="absolute -top-24 -left-24 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl pointer-events-none"
      />
      <motion.div 
        animate={{ 
          scale: [1, 1.5, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        className="absolute -bottom-24 -right-24 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"
      />

      <div className="relative z-10 px-8 md:px-12 w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-white mb-2">
            Market Intelligence
          </h1>
          <p className="text-muted-foreground text-lg md:text-xl max-w-2xl">
            Real-time global market data, advanced screening, and deep financial analysis.
          </p>
        </motion.div>
      </div>
    </div>
  );
}

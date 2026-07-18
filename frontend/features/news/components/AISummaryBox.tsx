"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AISummary } from '../types';
import { Sparkles, ShieldAlert, TrendingUp, TrendingDown, Target } from 'lucide-react';
import { motion } from 'framer-motion';

export function AISummaryBox({ summary }: { summary: AISummary }) {
  if (!summary) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 }}
      className="sticky top-[100px]"
    >
      <Card className="bg-card/60 backdrop-blur-xl border-white/10 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none -translate-y-1/2 translate-x-1/3" />
        
        <CardHeader className="pb-4 border-b border-white/5 relative z-10">
          <CardTitle className="text-sm font-semibold flex items-center">
            <Sparkles className="h-4 w-4 mr-2 text-indigo-400" />
            FinPilot AI Analysis
          </CardTitle>
        </CardHeader>
        
        <CardContent className="p-5 relative z-10 space-y-6">
          <div>
            <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-2">Executive Summary</h4>
            <p className="text-sm leading-relaxed text-foreground/90">{summary.executiveSummary}</p>
          </div>

          <div className="space-y-4">
            {summary.bullishSignals.length > 0 && (
              <div>
                <h4 className="text-[10px] font-bold text-emerald-500 uppercase tracking-wider mb-2 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" /> Bullish Signals
                </h4>
                <ul className="space-y-1">
                  {summary.bullishSignals.map((signal, i) => (
                    <li key={i} className="text-xs text-foreground/80 flex items-start">
                      <span className="text-emerald-500 mr-2 mt-0.5">•</span> {signal}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {summary.bearishSignals.length > 0 && (
              <div>
                <h4 className="text-[10px] font-bold text-destructive uppercase tracking-wider mb-2 flex items-center">
                  <TrendingDown className="h-3 w-3 mr-1" /> Bearish Signals
                </h4>
                <ul className="space-y-1">
                  {summary.bearishSignals.map((signal, i) => (
                    <li key={i} className="text-xs text-foreground/80 flex items-start">
                      <span className="text-destructive mr-2 mt-0.5">•</span> {signal}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-border/50">
            <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-2 flex items-center">
              <Target className="h-3 w-3 mr-1" /> Portfolio Impact
            </h4>
            <p className="text-sm text-foreground/90 italic">
              "{summary.portfolioImpact}"
            </p>
          </div>

          <div className="flex gap-4 pt-2">
            <div className="flex-1 bg-muted/30 p-2 rounded text-center border border-white/5">
              <div className="text-[10px] text-muted-foreground uppercase">Importance</div>
              <div className="font-bold text-lg text-indigo-400">{summary.importance}/10</div>
            </div>
            <div className="flex-1 bg-muted/30 p-2 rounded text-center border border-white/5">
              <div className="text-[10px] text-muted-foreground uppercase">Confidence</div>
              <div className="font-bold text-lg text-emerald-400">{summary.confidence}%</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

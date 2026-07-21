"use client";

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, ArrowDown, Settings2, Trash } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function VisualRuleBuilder() {
  const [nodes, setNodes] = useState([
    { id: '1', type: 'trigger', title: 'When...', subtitle: 'Portfolio value drops by 5%' },
    { id: '2', type: 'condition', title: 'If...', subtitle: 'Market hours are open' },
    { id: '3', type: 'action', title: 'Then...', subtitle: 'Send SMS Alert to +1 555-0100' }
  ]);

  const addNode = (type: string) => {
    setNodes([...nodes, { id: Date.now().toString(), type, title: 'New Step', subtitle: 'Configure settings' }]);
  };

  const removeNode = (id: string) => {
    setNodes(nodes.filter(n => n.id !== id));
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      <AnimatePresence>
        {nodes.map((node, index) => (
          <React.Fragment key={node.id}>
            <motion.div
              layout
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative"
            >
              <Card className="bg-card/60 backdrop-blur-xl border-white/10 shadow-lg group">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 shrink-0 rounded-lg flex items-center justify-center bg-indigo-500/10 border border-white/5">
                      <Settings2 className="h-5 w-5 text-indigo-400" />
                    </div>
                    <div>
                      <div className="font-semibold">{node.title}</div>
                      <div className="text-sm text-muted-foreground">{node.subtitle}</div>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => removeNode(node.id)} className="opacity-0 group-hover:opacity-100 transition-opacity hover:bg-destructive/20 hover:text-destructive text-muted-foreground">
                    <Trash className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            </motion.div>

            {index < nodes.length - 1 && (
              <div className="flex justify-center -my-2 relative z-10">
                <div className="bg-background border border-white/10 rounded-full p-1 text-muted-foreground">
                  <ArrowDown className="h-4 w-4" />
                </div>
              </div>
            )}
          </React.Fragment>
        ))}
      </AnimatePresence>

      <div className="pt-4 flex justify-center gap-4">
        <Button variant="outline" size="sm" onClick={() => addNode('condition')} className="border-white/10 bg-background/50 border-dashed">
          <Plus className="h-4 w-4 mr-1" /> Add Condition
        </Button>
        <Button variant="outline" size="sm" onClick={() => addNode('action')} className="border-white/10 bg-background/50 border-dashed">
          <Plus className="h-4 w-4 mr-1" /> Add Action
        </Button>
      </div>
    </div>
  );
}

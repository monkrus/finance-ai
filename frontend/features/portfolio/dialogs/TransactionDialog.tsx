import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface TransactionDialogProps {
  children: React.ReactNode;
  defaultTicker?: string;
}

export function TransactionDialog({ children, defaultTicker }: TransactionDialogProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px] bg-background/80 backdrop-blur-xl border-white/10 shadow-2xl">
        <DialogHeader>
          <DialogTitle>New Transaction</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="ticker" className="text-right">
              Ticker
            </Label>
            <Input id="ticker" defaultValue={defaultTicker} className="col-span-3 bg-card/50" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="action" className="text-right">
              Action
            </Label>
            <select id="action" className="col-span-3 flex h-10 w-full rounded-md border border-input bg-card/50 px-3 py-2 text-sm">
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
              <option value="dividend">Dividend</option>
            </select>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="shares" className="text-right">
              Shares
            </Label>
            <Input id="shares" type="number" className="col-span-3 bg-card/50" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="price" className="text-right">
              Price
            </Label>
            <Input id="price" type="number" className="col-span-3 bg-card/50" />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" className="w-full">Submit Order</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

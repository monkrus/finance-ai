"use client";

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Mail, Smartphone, Bell, Webhook, Info } from 'lucide-react';
import { usePreferences } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';

export function PreferenceMatrix() {
  const { data, isLoading, isError, refetch } = usePreferences();
  const [localData, setLocalData] = useState<any[] | null>(null);

  React.useEffect(() => {
    if (data) setLocalData(data);
  }, [data]);

  if (isError) return <WidgetError title="Preferences Error" message="Failed to load settings." onRetry={refetch} />;

  const toggle = (categoryId: string, channel: string) => {
    if (!localData) return;
    setLocalData(prev => prev!.map(p => {
      if (p.id === categoryId) {
        return { ...p, channels: { ...p.channels, [channel]: !p.channels[channel as keyof typeof p.channels] } };
      }
      return p;
    }));
  };

  const channels = [
    { id: 'email', icon: <Mail className="h-4 w-4" />, label: 'Email' },
    { id: 'push', icon: <Smartphone className="h-4 w-4" />, label: 'Push' },
    { id: 'inApp', icon: <Bell className="h-4 w-4" />, label: 'In-App' },
    { id: 'webhook', icon: <Webhook className="h-4 w-4" />, label: 'Webhook' }
  ];

  return (
    <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg overflow-hidden">
      <div className="overflow-x-auto custom-scrollbar">
        <table className="w-full text-sm text-left">
          <thead className="bg-muted/50 text-muted-foreground border-b border-white/5">
            <tr>
              <th className="px-6 py-4 font-semibold rounded-tl-xl w-1/3">Category</th>
              {channels.map(c => (
                <th key={c.id} className="px-6 py-4 font-semibold text-center">
                  <div className="flex flex-col items-center gap-2">
                    {c.icon}
                    {c.label}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {isLoading || !localData ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  <td className="px-6 py-4"><Skeleton className="h-5 w-32" /></td>
                  {channels.map(c => <td key={c.id} className="px-6 py-4"><Skeleton className="h-5 w-10 mx-auto rounded-full" /></td>)}
                </tr>
              ))
            ) : (
              localData.map(pref => (
                <tr key={pref.id} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 font-medium flex items-center gap-2">
                    {pref.category}
                    <Info className="h-3 w-3 text-muted-foreground opacity-50 cursor-help" />
                  </td>
                  {channels.map(c => (
                    <td key={c.id} className="px-6 py-4 text-center">
                      <div className="flex justify-center">
                        <Switch 
                          checked={pref.channels[c.id]} 
                          onCheckedChange={() => toggle(pref.id, c.id)} 
                        />
                      </div>
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

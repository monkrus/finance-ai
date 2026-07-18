"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { 
  User, Shield, BellRing, Network, Key, Palette, 
  Globe, Activity, History, Server, Blocks, Search
} from 'lucide-react';
import { Input } from '@/components/ui/input';

const navGroups = [
  {
    title: 'Account',
    items: [
      { name: 'Profile', href: '/settings', icon: <User className="h-4 w-4" /> },
      { name: 'Security', href: '/settings/security', icon: <Shield className="h-4 w-4" /> },
      { name: 'Notifications', href: '/settings/notifications', icon: <BellRing className="h-4 w-4" /> },
    ]
  },
  {
    title: 'Platform',
    items: [
      { name: 'Integrations', href: '/settings/integrations', icon: <Network className="h-4 w-4" /> },
      { name: 'API Keys', href: '/settings/api-keys', icon: <Key className="h-4 w-4" /> },
      { name: 'Appearance', href: '/settings/appearance', icon: <Palette className="h-4 w-4" /> },
      { name: 'Localization', href: '/settings/localization', icon: <Globe className="h-4 w-4" /> },
    ]
  },
  {
    title: 'Admin',
    items: [
      { name: 'Usage', href: '/settings/usage', icon: <Activity className="h-4 w-4" /> },
      { name: 'Audit Logs', href: '/settings/audit', icon: <History className="h-4 w-4" /> },
      { name: 'Admin Dashboard', href: '/settings/admin', icon: <Server className="h-4 w-4" /> },
      { name: 'Organization', href: '/settings/organization', icon: <Blocks className="h-4 w-4" /> },
    ]
  }
];

export function SettingsSidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 border-r border-white/5 bg-card/40 flex flex-col h-full shrink-0">
      <div className="p-4 border-b border-white/5">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search settings..." 
            className="pl-9 h-9 bg-background/50 border-white/10 text-sm"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-6">
        {navGroups.map(group => (
          <div key={group.title} className="space-y-1">
            <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground px-2 mb-2">{group.title}</div>
            {group.items.map(item => {
              const isActive = pathname === item.href;
              return (
                <Link 
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "relative flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                    isActive ? "text-indigo-100" : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                  )}
                >
                  {isActive && (
                    <motion.div
                      layoutId="active-setting"
                      className="absolute inset-0 bg-indigo-500/20 rounded-lg"
                      initial={false}
                      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    />
                  )}
                  <div className="relative z-10 flex items-center gap-3">
                    <div className={cn(isActive ? "text-indigo-400" : "opacity-70")}>{item.icon}</div>
                    {item.name}
                  </div>
                </Link>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

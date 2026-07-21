"use client";

import React from 'react';
import { useSecurityStatus } from '../api/queries';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { ShieldCheck, ShieldAlert, Key, Smartphone, Monitor, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

export function SecurityCenter() {
  const { data, isLoading, isError, refetch } = useSecurityStatus();

  if (isError) return <WidgetError title="Security Error" message="Failed to load security status." onRetry={refetch} />;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
      <div>
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight">Security Center</h2>
        <p className="text-muted-foreground mt-1">Manage passwords, two-factor authentication, and active sessions.</p>
      </div>

      {isLoading || !data ? (
        <div className="space-y-6">
          <Skeleton className="h-[120px] w-full rounded-2xl" />
          <Skeleton className="h-[300px] w-full rounded-2xl" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Security Score Hero */}
          <Card className={cn(
            "backdrop-blur-xl border-white/10 shadow-lg overflow-hidden relative",
            data.securityScore > 80 ? "bg-emerald-500/10" : data.securityScore > 50 ? "bg-amber-500/10" : "bg-destructive/10"
          )}>
            <div className="absolute top-0 right-0 w-64 h-64 bg-current opacity-20 blur-[100px] rounded-full translate-x-1/2 -translate-y-1/2" />
            <CardContent className="p-6 md:p-8 flex items-center justify-between relative z-10">
              <div className="flex items-center gap-6">
                <div className="shrink-0 relative">
                  <svg className="w-24 h-24 transform -rotate-90">
                    <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="opacity-20" />
                    <motion.circle 
                      cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" 
                      strokeDasharray={251.2} 
                      initial={{ strokeDashoffset: 251.2 }}
                      animate={{ strokeDashoffset: 251.2 - (251.2 * data.securityScore) / 100 }}
                      transition={{ duration: 1.5, ease: "easeOut" }}
                      className={cn(data.securityScore > 80 ? "text-emerald-500" : data.securityScore > 50 ? "text-amber-500" : "text-destructive")}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center flex-col">
                    <span className="text-2xl font-bold">{data.securityScore}</span>
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-semibold flex items-center gap-2">
                    Security Strength
                    {data.securityScore > 80 ? <ShieldCheck className="h-5 w-5 text-emerald-500" /> : <ShieldAlert className="h-5 w-5 text-amber-500" />}
                  </h3>
                  <p className="text-muted-foreground mt-1 max-w-sm">
                    {data.securityScore > 80 ? "Your account security is excellent. Keep it up!" : "Enhance your security by enabling 2FA and reviewing sessions."}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Core Security Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="h-5 w-5 text-indigo-400" />
                  Password
                </CardTitle>
                <CardDescription>Last changed 3 months ago</CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex items-end">
                <Button variant="outline" className="w-full bg-background/50 border-white/10">Change Password</Button>
              </CardContent>
            </Card>

            <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Smartphone className="h-5 w-5 text-indigo-400" />
                  Two-Factor Authentication
                </CardTitle>
                <CardDescription>
                  {data.twoFactorEnabled ? "2FA is currently enabled for your account." : "Protect your account with an extra layer of security."}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex items-end">
                {data.twoFactorEnabled ? (
                  <Button variant="outline" className="w-full bg-background/50 border-white/10 text-destructive hover:bg-destructive/10 hover:text-destructive border-destructive/20">Disable 2FA</Button>
                ) : (
                  <Button className="w-full bg-indigo-600 hover:bg-indigo-700">Enable 2FA</Button>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Active Sessions */}
          <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
            <CardHeader>
              <CardTitle>Active Sessions</CardTitle>
              <CardDescription>Devices that are currently logged into your account.</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-border/50">
                <AnimatePresence>
                  {data.activeSessions.map((session, index) => (
                    <motion.div 
                      key={session.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center justify-between p-4 hover:bg-white/5 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="h-10 w-10 shrink-0 rounded-full bg-background/50 border border-white/10 flex items-center justify-center">
                          {session.device.toLowerCase().includes('mobile') ? <Smartphone className="h-5 w-5 text-muted-foreground" /> : <Monitor className="h-5 w-5 text-muted-foreground" />}
                        </div>
                        <div>
                          <div className="font-semibold flex items-center gap-2">
                            {session.device} • {session.browser}
                            {session.isCurrent && (
                              <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400">Current</span>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1 flex flex-col sm:flex-row sm:items-center sm:gap-2">
                            <span>{session.location}</span>
                            <span className="hidden sm:inline">•</span>
                            <span>{session.ip}</span>
                            <span className="hidden sm:inline">•</span>
                            <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {formatDistanceToNow(new Date(session.lastActive), { addSuffix: true })}</span>
                          </div>
                        </div>
                      </div>
                      {!session.isCurrent && (
                        <Button variant="ghost" size="sm" className="text-destructive hover:bg-destructive/10 hover:text-destructive">Revoke</Button>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </motion.div>
  );
}

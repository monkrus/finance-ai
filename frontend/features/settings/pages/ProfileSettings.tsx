"use client";

import React from 'react';
import { useUserProfile, useUpdateProfile } from '../api/queries';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { User, Mail, Camera, Save } from 'lucide-react';
import { motion } from 'framer-motion';

export function ProfileSettings() {
  const { data, isLoading, isError, refetch } = useUserProfile();
  const { mutate: updateProfile, isPending } = useUpdateProfile();

  if (isError) return <WidgetError title="Profile Error" message="Failed to load profile." onRetry={refetch} />;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Gather form data and submit
    updateProfile({});
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
      <div>
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight">Public Profile</h2>
        <p className="text-muted-foreground mt-1">Manage your personal information and how others see you on FinPilot.</p>
      </div>

      {isLoading || !data ? (
        <div className="space-y-6">
          <Skeleton className="h-[200px] w-full rounded-2xl" />
          <Skeleton className="h-[400px] w-full rounded-2xl" />
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Avatar Section */}
          <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
            <CardContent className="p-6 flex flex-col md:flex-row gap-6 items-center md:items-start">
              <div className="relative group">
                <div className="h-24 w-24 rounded-full bg-indigo-500/20 border-2 border-indigo-500/50 flex items-center justify-center overflow-hidden">
                  {data.avatarUrl ? (
                    <img src={data.avatarUrl} alt="Avatar" className="w-full h-full object-cover" />
                  ) : (
                    <User className="h-10 w-10 text-indigo-400" />
                  )}
                </div>
                <button type="button" className="absolute inset-0 bg-black/60 rounded-full flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                  <Camera className="h-5 w-5 text-white mb-1" />
                  <span className="text-[10px] text-white/90">Change</span>
                </button>
              </div>
              <div className="flex-1 text-center md:text-left space-y-1">
                <h3 className="font-semibold text-lg">{data.name}</h3>
                <p className="text-sm text-muted-foreground flex items-center justify-center md:justify-start gap-1">
                  <Mail className="h-3 w-3" /> {data.email}
                </p>
                <div className="pt-2">
                  <Button variant="outline" size="sm" className="bg-background/50 border-white/10">Remove Photo</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Form Fields */}
          <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
              <CardDescription>Update your personal details and contact information.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" defaultValue={data.name} className="bg-background/50 border-white/10" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input id="username" defaultValue={data.username} className="bg-background/50 border-white/10" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input id="email" type="email" defaultValue={data.email} className="bg-background/50 border-white/10" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input id="phone" type="tel" defaultValue={data.phone} className="bg-background/50 border-white/10" />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea id="bio" defaultValue={data.bio} rows={4} className="bg-background/50 border-white/10 resize-none" placeholder="A brief description of yourself..." />
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4 sticky bottom-8">
            <Button variant="outline" type="button" className="bg-background/80 backdrop-blur-md border-white/10 shadow-lg">Cancel</Button>
            <Button type="submit" disabled={isPending} className="bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-500/20">
              <Save className="h-4 w-4 mr-2" /> Save Changes
            </Button>
          </div>
        </form>
      )}
    </motion.div>
  );
}

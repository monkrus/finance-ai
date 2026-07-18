import { Metadata } from 'next';
import { SettingsSidebar } from '@/features/settings/components/SettingsSidebar';

export const metadata: Metadata = {
  title: 'Settings | FinPilot AI',
};

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-[calc(100vh-6rem)] overflow-hidden rounded-2xl border border-white/5 bg-background/50 backdrop-blur-3xl shadow-2xl">
      <SettingsSidebar />
      <div className="flex-1 overflow-y-auto custom-scrollbar relative">
        {/* Universal Ambient Background for Settings */}
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-indigo-500/5 rounded-full blur-[150px] pointer-events-none -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-fuchsia-500/5 rounded-full blur-[120px] pointer-events-none translate-y-1/3 -translate-x-1/3" />
        
        <main className="p-8 max-w-5xl mx-auto w-full relative z-10">
          {children}
        </main>
      </div>
    </div>
  );
}

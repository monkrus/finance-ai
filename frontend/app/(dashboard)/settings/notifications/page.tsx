import { PreferenceMatrix } from '@/features/notifications/preferences/PreferenceMatrix';

export default function SettingsNotificationsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight">Notification Preferences</h2>
        <p className="text-muted-foreground mt-1">Manage how and when you receive financial alerts.</p>
      </div>
      <PreferenceMatrix />
    </div>
  );
}

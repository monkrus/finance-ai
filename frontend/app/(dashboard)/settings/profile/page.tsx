import { Metadata } from 'next';
import { ProfileForm } from '@/features/auth/components/ProfileForm';

export const metadata: Metadata = {
  title: 'Profile Settings | FinPilot AI',
  description: 'Manage your profile settings',
};

export default function ProfilePage() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Profile</h3>
        <p className="text-sm text-muted-foreground">
          Update your public profile information and personal details.
        </p>
      </div>
      <div className="shrink-0 bg-border h-[1px] w-full" />
      <ProfileForm />
    </div>
  );
}

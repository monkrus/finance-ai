import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;
  
  // Basic notification state (for toast/drawers)
  notificationsCount: number;
  incrementNotifications: () => void;
  resetNotifications: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (isOpen) => set({ sidebarOpen: isOpen }),
  
  notificationsCount: 0,
  incrementNotifications: () => set((state) => ({ notificationsCount: state.notificationsCount + 1 })),
  resetNotifications: () => set({ notificationsCount: 0 }),
}));

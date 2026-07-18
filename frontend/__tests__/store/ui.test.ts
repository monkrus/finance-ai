import { useUIStore } from '@/store/ui';

describe('UI Store', () => {
  beforeEach(() => {
    // Reset state before each test
    useUIStore.setState({
      sidebarOpen: true,
      notificationsCount: 0,
    });
  });

  it('should toggle sidebar', () => {
    const { toggleSidebar } = useUIStore.getState();
    expect(useUIStore.getState().sidebarOpen).toBe(true);
    
    toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(false);
    
    toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(true);
  });

  it('should set sidebar open state directly', () => {
    const { setSidebarOpen } = useUIStore.getState();
    
    setSidebarOpen(false);
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });

  it('should increment notifications', () => {
    const { incrementNotifications } = useUIStore.getState();
    
    expect(useUIStore.getState().notificationsCount).toBe(0);
    incrementNotifications();
    expect(useUIStore.getState().notificationsCount).toBe(1);
  });

  it('should reset notifications', () => {
    useUIStore.setState({ notificationsCount: 5 });
    const { resetNotifications } = useUIStore.getState();
    
    resetNotifications();
    expect(useUIStore.getState().notificationsCount).toBe(0);
  });
});

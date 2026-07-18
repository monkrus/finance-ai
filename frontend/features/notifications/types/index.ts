export interface Notification {
  id: string;
  category: 'Portfolio' | 'Market' | 'News' | 'Wealth' | 'AI' | 'Integrations';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  summary: string;
  timestamp: string;
  status: 'unread' | 'read' | 'archived';
  source: string;
  relatedEntityId?: string;
}

export interface AutomationRule {
  id: string;
  name: string;
  status: 'active' | 'paused';
  lastExecution?: string;
  nextExecution?: string;
  trigger: {
    type: string;
    params: any;
  };
  conditions: any[];
  actions: any[];
}

export interface PreferenceSetting {
  id: string;
  category: string;
  channels: {
    email: boolean;
    push: boolean;
    inApp: boolean;
    webhook: boolean;
  };
  frequency: 'Instant' | 'Hourly' | 'Daily' | 'Weekly';
}

export interface ActivityEvent {
  id: string;
  type: 'rule_created' | 'rule_triggered' | 'delivered' | 'opened' | 'archived' | 'automation_executed';
  timestamp: string;
  description: string;
  status: 'success' | 'failed' | 'pending';
}

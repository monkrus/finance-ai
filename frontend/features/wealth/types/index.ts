// Wealth Architecture Types

export interface NetWorthSummary {
  totalAssets: number;
  totalLiabilities: number;
  netWorth: number;
  cash: number;
  investments: number;
  loans: number;
  credit: number;
  trend: 'up' | 'down' | 'neutral';
  changePercent: number;
}

export interface NetWorthHistoryItem {
  date: string;
  assets: number;
  liabilities: number;
  netWorth: number;
}

export interface Account {
  id: string;
  name: string;
  institution: string;
  type: 'Checking' | 'Savings' | 'Credit Card' | 'Investment' | 'Loan' | 'Mortgage';
  balance: number;
  currency: string;
  lastSync: string;
  status: 'connected' | 'disconnected' | 'error';
}

export interface Transaction {
  id: string;
  accountId: string;
  date: string;
  description: string;
  amount: number;
  category: string;
  type: 'income' | 'expense' | 'transfer' | 'investment';
  pending: boolean;
}

export interface BudgetSummary {
  totalBudget: number;
  totalSpent: number;
  remaining: number;
  utilizationPercent: number;
  burnRate: number;
  savingsRate: number;
}

export interface BudgetCategory {
  name: string;
  allocated: number;
  spent: number;
  remaining: number;
  status: 'under' | 'on-track' | 'over';
}

export interface CashFlowSummary {
  monthlyIncome: number;
  monthlyExpenses: number;
  freeCashFlow: number;
  incomeSources: { source: string; amount: number }[];
  expenseCategories: { category: string; amount: number }[];
}

export interface FinancialGoal {
  id: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  monthlyContribution: number;
  targetDate: string;
  category: 'Retirement' | 'Emergency' | 'House' | 'Car' | 'Education' | 'Other';
  probability: number; // 0-100
}

export interface WealthPlanSummary {
  fireProgress: number; // 0-100
  emergencyFundMonths: number;
  retirementReadiness: number; // 0-100
  debtToIncomeRatio: number;
  savingsRatio: number;
  healthScore: number; // 0-1000
}

export interface AICoachRecommendation {
  id: string;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  type: 'budget' | 'saving' | 'retirement' | 'goal' | 'general';
}

export interface WealthEvent {
  id: string;
  date: string;
  title: string;
  description: string;
  type: 'transaction' | 'milestone' | 'budget' | 'alert';
}

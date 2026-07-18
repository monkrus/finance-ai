import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import {
  NetWorthSummary,
  NetWorthHistoryItem,
  Account,
  Transaction,
  BudgetSummary,
  BudgetCategory,
  CashFlowSummary,
  FinancialGoal,
  WealthPlanSummary,
  AICoachRecommendation,
  WealthEvent
} from '../types';

/**
 * Wealth analytics live under /api/v1/wealth/analytics/* on the backend and use
 * snake_case aggregate shapes. These adapters map them onto the camelCase view
 * models the wealth widgets consume, keeping mapping in the API layer.
 */

interface BackendNetWorth {
  net_worth: number;
  total_assets: number;
  total_liabilities: number;
  assets: { cash: number; investments: number };
  liabilities: Record<string, number>;
}

interface BackendBudget {
  budgets: {
    category?: string;
    name?: string;
    amount?: number;
    allocated?: number;
    spent?: number;
  }[];
  total_spent: number;
  monthly_burn_rate_per_day: number;
  projected_monthly_spend: number;
}

interface BackendCashFlow {
  month: string;
  total_income: number;
  total_expenses: number;
  free_cash_flow: number;
  savings_rate_percentage: number;
  income_breakdown: Record<string, number>;
  expense_breakdown: Record<string, number>;
}

interface BackendPlanning {
  financial_health_score: number;
  emergency_fund_coverage_months: number;
  debt_to_income_ratio_percentage: number;
  savings_ratio_percentage: number;
  investment_ratio_percentage: number;
  retirement_readiness: {
    fire_target: number;
    current_investments: number;
    fire_progress_percentage: number;
  };
}

// Net Worth
export function useNetWorthSummary() {
  return useQuery({
    queryKey: ['wealth', 'networth', 'summary'],
    staleTime: 5 * 60 * 1000,
    queryFn: async (): Promise<NetWorthSummary> => {
      const res = await apiClient.get<BackendNetWorth>('/api/v1/wealth/analytics/networth');
      const d = res.data;
      const liabilities = d.liabilities ?? {};
      return {
        totalAssets: d.total_assets ?? 0,
        totalLiabilities: d.total_liabilities ?? 0,
        netWorth: d.net_worth ?? 0,
        cash: d.assets?.cash ?? 0,
        investments: d.assets?.investments ?? 0,
        loans: liabilities.loans ?? 0,
        credit: liabilities.credit ?? liabilities.credit_cards ?? 0,
        // The backend exposes no historical net-worth series, so no trend can
        // be derived; reported as neutral rather than invented.
        trend: 'neutral',
        changePercent: 0,
      };
    },
  });
}

export function useNetWorthHistory(range: string = '1Y') {
  return useQuery({
    queryKey: ['wealth', 'networth', 'history', range],
    staleTime: 60 * 60 * 1000,
    queryFn: async (): Promise<NetWorthHistoryItem[]> => {
      // No historical net-worth endpoint exists on the backend. Render the
      // current point rather than failing the whole chart.
      const res = await apiClient.get<BackendNetWorth>('/api/v1/wealth/analytics/networth');
      const d = res.data;
      return [
        {
          date: new Date().toISOString().slice(0, 10),
          assets: d.total_assets ?? 0,
          liabilities: d.total_liabilities ?? 0,
          netWorth: d.net_worth ?? 0,
        },
      ];
    },
  });
}

// Accounts
export function useAccounts() {
  return useQuery({
    queryKey: ['wealth', 'accounts'],
    staleTime: 5 * 60 * 1000,
    queryFn: async (): Promise<Account[]> => {
      const res = await apiClient.get<any[]>('/api/v1/wealth/accounts');
      return (res.data ?? []).map((a) => ({
        id: String(a.id),
        name: a.name ?? a.account_name ?? 'Account',
        institution: a.institution ?? a.provider ?? '—',
        type: (a.account_type ?? a.type ?? 'Checking') as Account['type'],
        balance: a.balance ?? a.current_balance ?? 0,
        currency: a.currency ?? 'USD',
        lastSync: a.last_synced_at ?? a.updated_at ?? new Date().toISOString(),
        status: 'connected',
      }));
    },
  });
}

// Transactions
interface TransactionParams {
  accountId?: string;
  category?: string;
  search?: string;
}

export function useTransactions(params: TransactionParams = {}) {
  return useInfiniteQuery({
    queryKey: ['wealth', 'transactions', params],
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.nextCursor || undefined,
    staleTime: 60 * 1000,
    queryFn: async () => {
      // Backend returns a plain array and does not paginate or filter server-side.
      const res = await apiClient.get<any[]>('/api/v1/wealth/transactions');
      let rows = res.data ?? [];

      if (params.category) {
        rows = rows.filter((t) => (t.category ?? '') === params.category);
      }
      if (params.accountId) {
        rows = rows.filter((t) => String(t.account_id ?? '') === params.accountId);
      }
      if (params.search) {
        const q = params.search.toLowerCase();
        rows = rows.filter((t) => (t.description ?? '').toLowerCase().includes(q));
      }

      const transactions: Transaction[] = rows.map((t) => ({
        id: String(t.id),
        accountId: String(t.account_id ?? ''),
        date: t.transaction_date ?? t.date ?? new Date().toISOString(),
        description: t.description ?? '—',
        amount: t.amount ?? 0,
        category: t.category ?? 'Uncategorized',
        type: (t.transaction_type ?? t.type ?? 'expense') as Transaction['type'],
        pending: false,
      }));

      return { transactions, nextCursor: undefined as number | undefined };
    },
  });
}

// Budget
export function useBudgetSummary() {
  return useQuery({
    queryKey: ['wealth', 'budget', 'summary'],
    staleTime: 5 * 60 * 1000,
    queryFn: async (): Promise<BudgetSummary> => {
      const [budgetRes, cashRes] = await Promise.all([
        apiClient.get<BackendBudget>('/api/v1/wealth/analytics/budget'),
        apiClient.get<BackendCashFlow>('/api/v1/wealth/analytics/cashflow'),
      ]);
      const b = budgetRes.data;
      const totalBudget = (b.budgets ?? []).reduce(
        (sum, x) => sum + (x.amount ?? x.allocated ?? 0),
        0
      );
      const totalSpent = b.total_spent ?? 0;
      return {
        totalBudget,
        totalSpent,
        remaining: totalBudget - totalSpent,
        utilizationPercent: totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0,
        burnRate: b.monthly_burn_rate_per_day ?? 0,
        savingsRate: cashRes.data?.savings_rate_percentage ?? 0,
      };
    },
  });
}

export function useBudgetCategories() {
  return useQuery({
    queryKey: ['wealth', 'budget', 'categories'],
    staleTime: 5 * 60 * 1000,
    queryFn: async (): Promise<BudgetCategory[]> => {
      const res = await apiClient.get<BackendBudget>('/api/v1/wealth/analytics/budget');
      return (res.data?.budgets ?? []).map((b) => {
        const allocated = b.amount ?? b.allocated ?? 0;
        const spent = b.spent ?? 0;
        const remaining = allocated - spent;
        const ratio = allocated > 0 ? spent / allocated : 0;
        return {
          name: b.category ?? b.name ?? 'Uncategorized',
          allocated,
          spent,
          remaining,
          status: ratio > 1 ? 'over' : ratio > 0.8 ? 'on-track' : 'under',
        };
      });
    },
  });
}

// Cash Flow
export function useCashFlowSummary(month?: string) {
  return useQuery({
    queryKey: ['wealth', 'cashflow', month],
    staleTime: 5 * 60 * 1000,
    queryFn: async (): Promise<CashFlowSummary> => {
      const res = await apiClient.get<BackendCashFlow>(
        `/api/v1/wealth/analytics/cashflow${month ? `?month=${month}` : ''}`
      );
      const d = res.data;
      return {
        monthlyIncome: d.total_income ?? 0,
        monthlyExpenses: d.total_expenses ?? 0,
        freeCashFlow: d.free_cash_flow ?? 0,
        incomeSources: Object.entries(d.income_breakdown ?? {}).map(([source, amount]) => ({
          source,
          amount,
        })),
        expenseCategories: Object.entries(d.expense_breakdown ?? {}).map(
          ([category, amount]) => ({ category, amount })
        ),
      };
    },
  });
}

// Goals
export function useFinancialGoals() {
  return useQuery({
    queryKey: ['wealth', 'goals'],
    staleTime: 5 * 60 * 1000,
    queryFn: async (): Promise<FinancialGoal[]> => {
      // GET /wealth/goals is POST-only on the backend; the read model lives
      // under analytics.
      const res = await apiClient.get<any>('/api/v1/wealth/analytics/goals');
      const rows = Array.isArray(res.data) ? res.data : res.data?.goals ?? [];
      return rows.map((g: any) => ({
        id: String(g.id ?? g.name),
        name: g.name ?? 'Goal',
        targetAmount: g.target_amount ?? 0,
        currentAmount: g.current_amount ?? 0,
        monthlyContribution: g.monthly_contribution ?? 0,
        targetDate: g.target_date ?? new Date().toISOString(),
        category: (g.category ?? 'Other') as FinancialGoal['category'],
        probability: g.probability ?? g.on_track_probability ?? 0,
      }));
    },
  });
}

// Planning
export function useWealthPlan() {
  return useQuery({
    queryKey: ['wealth', 'plan'],
    staleTime: 24 * 60 * 60 * 1000,
    queryFn: async (): Promise<WealthPlanSummary> => {
      const res = await apiClient.get<BackendPlanning>('/api/v1/wealth/analytics/planning');
      const d = res.data;
      return {
        fireProgress: d.retirement_readiness?.fire_progress_percentage ?? 0,
        emergencyFundMonths: d.emergency_fund_coverage_months ?? 0,
        retirementReadiness: d.retirement_readiness?.fire_progress_percentage ?? 0,
        debtToIncomeRatio: d.debt_to_income_ratio_percentage ?? 0,
        savingsRatio: d.savings_ratio_percentage ?? 0,
        healthScore: d.financial_health_score ?? 0,
      };
    },
  });
}

// AI Coach
export function useAICoach() {
  return useQuery({
    queryKey: ['wealth', 'coach'],
    staleTime: 60 * 60 * 1000,
    retry: false,
    queryFn: async (): Promise<AICoachRecommendation[]> => {
      const res = await apiClient.get<any>('/api/v1/wealth/coach/advice', {
        params: { query: 'Give me recommendations to improve my financial health.' },
      });
      const advice = res.data?.advice ?? res.data?.answer ?? res.data;
      if (!advice) return [];
      return [
        {
          id: 'coach-advice',
          title: 'FinPilot AI Coach',
          description: typeof advice === 'string' ? advice : JSON.stringify(advice),
          impact: 'medium',
          type: 'general',
        },
      ];
    },
  });
}

// Timeline
export function useWealthTimeline() {
  return useQuery({
    queryKey: ['wealth', 'timeline'],
    staleTime: 5 * 60 * 1000,
    queryFn: async (): Promise<WealthEvent[]> => {
      // No wealth timeline/event endpoint exists on the backend. Derive the
      // timeline from real wealth transactions rather than inventing events.
      const res = await apiClient.get<any[]>('/api/v1/wealth/transactions');
      return (res.data ?? []).map((t) => ({
        id: String(t.id),
        date: t.transaction_date ?? t.date ?? new Date().toISOString(),
        title: t.description ?? 'Transaction',
        description: `${t.category ?? 'Uncategorized'} — ${t.amount ?? 0}`,
        type: 'transaction',
      }));
    },
  });
}

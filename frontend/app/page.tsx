import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  PieChart,
  LineChart,
  Newspaper,
  Wallet,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';

const features = [
  {
    icon: PieChart,
    title: 'Portfolio Management',
    description: 'Track holdings, allocation, and performance with risk analytics.',
  },
  {
    icon: LineChart,
    title: 'Market Intelligence',
    description: 'Quotes, fundamentals, valuation models, and peer comparison.',
  },
  {
    icon: Newspaper,
    title: 'News Intelligence',
    description: 'Curated market news with AI sentiment and portfolio impact.',
  },
  {
    icon: Wallet,
    title: 'Wealth Management',
    description: 'Net worth, cash flow, budgets, and financial goal planning.',
  },
  {
    icon: Sparkles,
    title: 'AI Copilot',
    description: 'Grounded answers over your portfolio, documents, and the market.',
  },
  {
    icon: ShieldCheck,
    title: 'Secure by Design',
    description: 'Argon2 hashing, refresh-token rotation, and role-based access.',
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-background relative overflow-hidden">
      {/* Background decorators, matching the auth layout's visual language */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/10 blur-3xl" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-accent/10 blur-3xl" />

      <div className="relative z-10">
        {/* Navigation */}
        <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <Link href="/" className="text-xl font-bold tracking-tight">
            FinPilot AI
          </Link>
          <nav className="flex items-center gap-3">
            <Button variant="ghost" asChild>
              <Link href="/login">Sign in</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Get started</Link>
            </Button>
          </nav>
        </header>

        {/* Hero */}
        <section className="mx-auto max-w-4xl px-6 pt-16 pb-14 text-center">
          <h1 className="text-4xl font-extrabold leading-tight tracking-tight md:text-6xl">
            Intelligence for the
            <br />
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Modern Investor
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            FinPilot AI unifies your portfolio, market research, news, and wealth planning
            into one AI-powered workspace.
          </p>

          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button size="lg" asChild>
              <Link href="/register">
                Create your account
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/login">Sign in to your account</Link>
            </Button>
          </div>

          <p className="mt-5 text-sm text-muted-foreground">
            Already signed in?{' '}
            <Link href="/dashboard" className="font-medium text-foreground hover:underline">
              Go to your dashboard
            </Link>
          </p>
        </section>

        {/* Feature grid */}
        <section className="mx-auto max-w-6xl px-6 pb-24">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {features.map(({ icon: Icon, title, description }) => (
              <div
                key={title}
                className="glass-panel rounded-2xl p-6 transition-colors hover:bg-card/60"
              >
                <div className="mb-4 inline-flex rounded-full bg-primary/10 p-3 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <h2 className="mb-1 font-semibold">{title}</h2>
                <p className="text-sm text-muted-foreground">{description}</p>
              </div>
            ))}
          </div>
        </section>

        <footer className="border-t border-border/50 py-8 text-center text-sm text-muted-foreground">
          FinPilot AI — Intelligent Wealth Management
        </footer>
      </div>
    </main>
  );
}

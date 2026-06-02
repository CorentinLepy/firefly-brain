import Link from "next/link";
import { StatCard } from "../components/StatCard";
import { apiGet } from "../lib/api";

type AlertItem = { type: string; severity: string; title: string; message: string };
type Subscription = { merchant: string; amount: number; frequency: string; yearly_cost: number; confidence: number; next_expected: string };
type Opportunity = { type: string; title: string; message: string; potential_saving: number };
type DashboardSummary = {
  period: { start: string; end: string };
  income: number;
  expenses: number;
  savings: number;
  savings_rate: number;
  expense_ratio: number;
  transfers: number;
  gross_assets: number;
  total_liabilities: number;
  net_worth: number;
  available_cash: number;
  uncategorized_transactions: number;
  transactions_count: number;
  accounts_count: number;
  budgets_count: number;
  subscriptions_count: number;
  subscriptions_yearly_cost: number;
  alerts_count: number;
  alerts: AlertItem[];
  top_categories: { category: string; amount: number }[];
  top_merchants: { merchant: string; amount: number }[];
  daily_expenses: { date: string; amount: number }[];
};
type InsightOverview = { subscriptions: Subscription[]; optimization_opportunities: Opportunity[] };
type GoalSummary = { count: number; items: { id: number; name: string; target_amount: number; current_amount: number; remaining_amount: number; progress: number; target_date: string | null }[] };
type AssetSummary = { total: number; items: unknown[] };
type LiabilitySummary = { total_remaining: number; total_monthly_payment: number; items: unknown[] };

function money(value: number) {
  return new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(value || 0);
}

function percent(value: number) {
  return new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 }).format(value || 0) + " %";
}

function ratio(part: number, total: number) {
  if (!total || total <= 0) return 0;
  return Math.min(100, Math.round((part / total) * 100));
}

function score(summary: DashboardSummary | null) {
  if (!summary) return { label: "Indisponible", value: 0 };
  let value = 50;
  if (summary.savings_rate >= 20) value += 20;
  else if (summary.savings_rate >= 10) value += 10;
  else if (summary.savings_rate < 0) value -= 20;
  if (summary.net_worth > 0) value += 15;
  else value -= 10;
  if (summary.uncategorized_transactions === 0) value += 5;
  if (summary.alerts_count > 0) value -= Math.min(20, summary.alerts_count * 5);
  const bounded = Math.max(0, Math.min(100, value));
  return { label: `${bounded}/100`, value: bounded };
}

export default async function Home() {
  let summary: DashboardSummary | null = null;
  let insights: InsightOverview | null = null;
  let goals: GoalSummary | null = null;
  let assets: AssetSummary | null = null;
  let liabilities: LiabilitySummary | null = null;
  let error: string | null = null;

  try {
    [summary, insights, goals, assets, liabilities] = await Promise.all([
      apiGet<DashboardSummary>("/api/dashboard/summary?start=2026-05-01&end=2026-05-31"),
      apiGet<InsightOverview>("/api/insights/overview?start=2026-05-01&end=2026-05-31"),
      apiGet<GoalSummary>("/api/goals"),
      apiGet<AssetSummary>("/api/assets"),
      apiGet<LiabilitySummary>("/api/liabilities"),
    ]);
  } catch (err) {
    error = err instanceof Error ? err.message : "Erreur inconnue";
  }

  const financialScore = score(summary);
  const maxCategory = Math.max(...(summary?.top_categories ?? []).map((item) => item.amount), 0);
  const maxMerchant = Math.max(...(summary?.top_merchants ?? []).map((item) => item.amount), 0);

  return (
    <main className="page">
      <nav className="topnav">
        <strong>Firefly Brain V2.1.1</strong>
        <Link href="/">Dashboard</Link>
        <Link href="/abonnements">Abonnements</Link>
        <Link href="/alertes">Alertes</Link>
        <Link href="/patrimoine">Patrimoine</Link>
        <Link href="/transactions">Transactions</Link>
      </nav>

      <section className="header">
        <div>
          <div className="eyebrow">Copilote financier personnel</div>
          <h1>Vue globale claire, exploitable et connectée à Firefly III</h1>
          <p>Analyse Firefly III enrichie : patrimoine, cash-flow, abonnements détectés, alertes, objectifs et pistes d'optimisation.</p>
          {summary?.period ? <p>Période analysée : {summary.period.start} → {summary.period.end}</p> : null}
        </div>
        <div className="score-card">
          <span>Score financier</span>
          <strong>{financialScore.label}</strong>
          <div className="progress"><i style={{ width: `${financialScore.value}%` }} /></div>
        </div>
      </section>

      {error ? (
        <div className="card danger-card">
          <strong>Connexion API indisponible</strong>
          <p>{error}</p>
          <p>Vérifie le backend, NEXT_PUBLIC_API_URL et backend/.env.</p>
        </div>
      ) : null}

      <section className="hero-grid">
        <div className="card hero-card">
          <div className="label">Patrimoine net Firefly</div>
          <div className="hero-value">{money(summary?.net_worth ?? 0)}</div>
          <p>Actifs inclus dans le patrimoine moins dettes incluses.</p>
          <div className="split"><span>Actifs {money(summary?.gross_assets ?? 0)}</span><span>Dettes {money(summary?.total_liabilities ?? 0)}</span></div>
        </div>
        <div className="card hero-card">
          <div className="label">Épargne période</div>
          <div className="hero-value">{money(summary?.savings ?? 0)}</div>
          <p>Taux d'épargne : {percent(summary?.savings_rate ?? 0)}</p>
          <div className="progress"><i style={{ width: `${Math.max(0, Math.min(summary?.savings_rate ?? 0, 100))}%` }} /></div>
        </div>
        <div className="card hero-card">
          <div className="label">Abonnements détectés</div>
          <div className="hero-value">{summary?.subscriptions_count ?? 0}</div>
          <p>Coût annuel estimé : {money(summary?.subscriptions_yearly_cost ?? 0)}</p>
        </div>
      </section>

      <section className="grid">
        <StatCard label="Revenus" value={money(summary?.income ?? 0)} />
        <StatCard label="Dépenses" value={money(summary?.expenses ?? 0)} hint={`${summary?.expense_ratio ?? 0} % des revenus`} />
        <StatCard label="Cash disponible" value={money(summary?.available_cash ?? 0)} />
        <StatCard label="Alertes" value={`${summary?.alerts_count ?? 0}`} />
        <StatCard label="À catégoriser" value={`${summary?.uncategorized_transactions ?? 0}`} />
        <StatCard label="Transactions" value={`${summary?.transactions_count ?? 0}`} />
        <StatCard label="Objectifs" value={`${goals?.count ?? 0}`} />
        <StatCard label="Mensualités manuelles" value={money(liabilities?.total_monthly_payment ?? 0)} />
      </section>

      <section className="section three">
        <div className="card">
          <h2>Alertes intelligentes</h2>
          <div className="list">
            {(summary?.alerts ?? []).map((item) => <div className={`alert ${item.severity}`} key={item.type}><strong>{item.title}</strong><p>{item.message}</p></div>)}
            {(summary?.alerts ?? []).length === 0 ? <p>Aucune alerte critique sur la période.</p> : null}
          </div>
        </div>
        <div className="card">
          <h2>Pistes d'optimisation</h2>
          <div className="list">
            {(insights?.optimization_opportunities ?? []).slice(0, 5).map((item) => <div className="mini" key={item.title}><strong>{item.title}</strong><p>{item.message}</p></div>)}
          </div>
        </div>
        <div className="card">
          <h2>Données Firefly Brain</h2>
          <p>Actifs manuels : {money(assets?.total ?? 0)}</p>
          <p>Dettes manuelles : {money(liabilities?.total_remaining ?? 0)}</p>
          <p>Objectifs suivis : {goals?.count ?? 0}</p>
        </div>
      </section>

      <section className="section">
        <div className="card">
          <h2>Top catégories</h2>
          <div className="list">
            {(summary?.top_categories ?? []).map((item) => <div className="metric-row" key={item.category}><div className="row"><span>{item.category}</span><strong>{money(item.amount)}</strong></div><div className="progress small"><i style={{ width: `${ratio(item.amount, maxCategory)}%` }} /></div></div>)}
          </div>
        </div>
        <div className="card">
          <h2>Top marchands</h2>
          <div className="list">
            {(summary?.top_merchants ?? []).map((item) => <div className="metric-row" key={item.merchant}><div className="row"><span>{item.merchant}</span><strong>{money(item.amount)}</strong></div><div className="progress small"><i style={{ width: `${ratio(item.amount, maxMerchant)}%` }} /></div></div>)}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="card">
          <h2>Abonnements probables</h2>
          <div className="table">
            <div className="table-row head"><span>Marchand</span><span>Montant</span><span>Fréquence</span><span>Annuel</span></div>
            {(insights?.subscriptions ?? []).slice(0, 8).map((item) => <div className="table-row" key={`${item.merchant}-${item.amount}`}><span>{item.merchant}</span><span>{money(item.amount)}</span><span>{item.frequency}</span><strong>{money(item.yearly_cost)}</strong></div>)}
          </div>
        </div>
        <div className="card">
          <h2>Objectifs financiers</h2>
          {(goals?.items ?? []).length === 0 ? <p>Aucun objectif créé. Utilise l'API /api/goals pour en ajouter en V2.</p> : null}
          {(goals?.items ?? []).map((goal) => <div className="metric-row" key={goal.id}><div className="row"><span>{goal.name}</span><strong>{goal.progress}%</strong></div><div className="progress small"><i style={{ width: `${Math.min(goal.progress, 100)}%` }} /></div><p>Reste : {money(goal.remaining_amount)}</p></div>)}
        </div>
      </section>
    </main>
  );
}

import { StatCard } from "../components/StatCard";
import { apiGet } from "../lib/api";

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
  top_categories: { category: string; amount: number }[];
  top_merchants: { merchant: string; amount: number }[];
};

type AssetSummary = { total: number; items: unknown[] };
type LiabilitySummary = { total_remaining: number; total_monthly_payment: number; items: unknown[] };

function money(value: number) {
  return new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(value);
}

export default async function Home() {
  let summary: DashboardSummary | null = null;
  let assets: AssetSummary | null = null;
  let liabilities: LiabilitySummary | null = null;
  let error: string | null = null;

  try {
    [summary, assets, liabilities] = await Promise.all([
      apiGet<DashboardSummary>("/api/dashboard/summary"),
      apiGet<AssetSummary>("/api/assets"),
      apiGet<LiabilitySummary>("/api/liabilities"),
    ]);
  } catch (err) {
    error = err instanceof Error ? err.message : "Erreur inconnue";
  }

  return (
    <main className="page">
      <div className="header">
        <div>
          <div className="eyebrow">Firefly Brain MVP V1.1</div>
          <h1>Pilotage financier personnel</h1>
          <p>Dashboard moderne compatible Firefly III : revenus, dépenses, patrimoine, crédits et reste à vivre.</p>
          {summary?.period ? <p>Période analysée : {summary.period.start} → {summary.period.end}</p> : null}
        </div>
        <div className="badge">Connecté à Firefly III</div>
      </div>

      {error ? (
        <div className="card">
          <strong>Connexion API indisponible</strong>
          <p>{error}</p>
          <p>Vérifie que le backend est lancé et que le token Firefly III est configuré dans backend/.env.</p>
        </div>
      ) : null}

      <section className="grid">
        <StatCard label="Revenus période" value={money(summary?.income ?? 0)} />
        <StatCard label="Dépenses période" value={money(summary?.expenses ?? 0)} hint={`${summary?.expense_ratio ?? 0} % des revenus`} />
        <StatCard label="Épargne estimée" value={money(summary?.savings ?? 0)} hint={`${summary?.savings_rate ?? 0} % de taux d'épargne`} />
        <StatCard label="Patrimoine net Firefly" value={money(summary?.net_worth ?? 0)} hint="Actifs Firefly - dettes Firefly" />
        <StatCard label="Patrimoine brut" value={money(summary?.gross_assets ?? 0)} />
        <StatCard label="Dettes Firefly" value={money(summary?.total_liabilities ?? 0)} />
        <StatCard label="Argent disponible" value={money(summary?.available_cash ?? 0)} />
        <StatCard label="Transactions à catégoriser" value={`${summary?.uncategorized_transactions ?? 0}`} />
        <StatCard label="Transactions analysées" value={`${summary?.transactions_count ?? 0}`} />
        <StatCard label="Comptes Firefly" value={`${summary?.accounts_count ?? 0}`} />
        <StatCard label="Budgets Firefly" value={`${summary?.budgets_count ?? 0}`} />
        <StatCard label="Transferts internes" value={money(summary?.transfers ?? 0)} />
      </section>

      <section className="section">
        <div className="card">
          <h2>Top catégories de dépenses</h2>
          <div className="list">
            {(summary?.top_categories ?? []).map((item) => (
              <div className="row" key={item.category}>
                <span>{item.category}</span>
                <strong>{money(item.amount)}</strong>
              </div>
            ))}
            {summary?.top_categories.length === 0 ? <p>Aucune catégorie à afficher pour le moment.</p> : null}
          </div>
        </div>

        <div className="card">
          <h2>Top marchands</h2>
          <div className="list">
            {(summary?.top_merchants ?? []).map((item) => (
              <div className="row" key={item.merchant}>
                <span>{item.merchant}</span>
                <strong>{money(item.amount)}</strong>
              </div>
            ))}
            {summary?.top_merchants.length === 0 ? <p>Aucun marchand à afficher pour le moment.</p> : null}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="card">
          <h2>Données manuelles Firefly Brain</h2>
          <p>Actifs manuels : {money(assets?.total ?? 0)}</p>
          <p>Dettes manuelles : {money(liabilities?.total_remaining ?? 0)}</p>
          <p>Mensualités manuelles : {money(liabilities?.total_monthly_payment ?? 0)}</p>
        </div>

        <div className="card">
          <h2>Prochaines priorités</h2>
          <p>1. Ajouter la page paramètres Firefly III.</p>
          <p>2. Ajouter une vraie synchronisation locale PostgreSQL.</p>
          <p>3. Ajouter les graphiques et filtres de période.</p>
          <p>4. Ajouter le calcul avancé du reste à vivre.</p>
        </div>
      </section>
    </main>
  );
}

import { StatCard } from "../components/StatCard";
import { apiGet } from "../lib/api";

type DashboardSummary = {
  income: number;
  expenses: number;
  savings: number;
  savings_rate: number;
  uncategorized_transactions: number;
  top_categories: { category: string; amount: number }[];
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

  const netWorth = (assets?.total ?? 0) - (liabilities?.total_remaining ?? 0);

  return (
    <main className="page">
      <div className="header">
        <div>
          <div className="eyebrow">Firefly Brain MVP</div>
          <h1>Pilotage financier personnel</h1>
          <p>Surcouche moderne compatible Firefly III : revenus, dépenses, patrimoine, crédits et reste à vivre.</p>
        </div>
        <div className="badge">Mode MVP lecture + saisie manuelle</div>
      </div>

      {error ? (
        <div className="card">
          <strong>Connexion API indisponible</strong>
          <p>{error}</p>
          <p>Vérifie que le backend est lancé et que le token Firefly III est configuré dans backend/.env.</p>
        </div>
      ) : null}

      <section className="grid">
        <StatCard label="Revenus du mois" value={money(summary?.income ?? 0)} />
        <StatCard label="Dépenses du mois" value={money(summary?.expenses ?? 0)} />
        <StatCard label="Épargne estimée" value={money(summary?.savings ?? 0)} hint={`${summary?.savings_rate ?? 0} % de taux d'épargne`} />
        <StatCard label="Patrimoine net" value={money(netWorth)} hint="Actifs manuels - dettes manuelles" />
        <StatCard label="Actifs" value={money(assets?.total ?? 0)} />
        <StatCard label="Dettes restantes" value={money(liabilities?.total_remaining ?? 0)} />
        <StatCard label="Mensualités crédit" value={money(liabilities?.total_monthly_payment ?? 0)} />
        <StatCard label="Transactions à catégoriser" value={`${summary?.uncategorized_transactions ?? 0}`} />
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
          <h2>Prochaines priorités</h2>
          <p>1. Configurer Firefly III dans le backend.</p>
          <p>2. Ajouter les premiers actifs et crédits via Swagger.</p>
          <p>3. Brancher les formulaires frontend.</p>
          <p>4. Ajouter le calcul réel du reste à vivre.</p>
        </div>
      </section>
    </main>
  );
}

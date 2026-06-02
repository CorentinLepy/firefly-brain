import Link from "next/link";
import { apiGet } from "../../lib/api";

type Subscription = {
  merchant: string;
  amount: number;
  frequency: string;
  occurrences: number;
  last_seen: string;
  next_expected: string;
  yearly_cost: number;
  confidence: number;
  category?: string | null;
  budget?: string | null;
};
type SubscriptionResponse = { count: number; monthly_cost_detected: number; yearly_cost_detected: number; items: Subscription[] };

function money(value: number) {
  return new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(value || 0);
}

export default async function SubscriptionsPage() {
  const data = await apiGet<SubscriptionResponse>("/api/subscriptions/detect?start=2026-01-01&end=2026-05-31");
  return (
    <main className="page">
      <nav className="topnav"><strong>Firefly Brain V2.1</strong><Link href="/">Dashboard</Link><Link href="/alertes">Alertes</Link><Link href="/patrimoine">Patrimoine</Link></nav>
      <section className="header compact"><div><div className="eyebrow">Abonnements</div><h1>Charges récurrentes détectées</h1><p>La V2.1 filtre les crédits, prêts, dettes et achats exceptionnels pour réduire les faux positifs.</p></div></section>
      <section className="grid"><div className="stat-card"><div className="stat-label">Abonnements probables</div><div className="stat-value">{data.count}</div></div><div className="stat-card"><div className="stat-label">Coût mensuel détecté</div><div className="stat-value">{money(data.monthly_cost_detected)}</div></div><div className="stat-card"><div className="stat-label">Coût annuel estimé</div><div className="stat-value">{money(data.yearly_cost_detected)}</div></div></section>
      <section className="section single"><div className="card"><h2>Liste à valider</h2><div className="table"><div className="table-row head"><span>Marchand</span><span>Montant</span><span>Fréquence</span><span>Confiance</span><span>Annuel</span></div>{data.items.map((item) => <div className="table-row five" key={`${item.merchant}-${item.amount}-${item.frequency}`}><span>{item.merchant}<small>{item.category ? `Catégorie : ${item.category}` : ""}</small></span><span>{money(item.amount)}</span><span>{item.frequency}</span><span>{item.confidence}%</span><strong>{money(item.yearly_cost)}</strong></div>)}</div>{data.items.length === 0 ? <p>Aucun abonnement probable détecté sur la période.</p> : null}</div></section>
    </main>
  );
}
